from flask import Flask, render_template, request, redirect, session
import mysql.connector
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

app = Flask(__name__)

app.secret_key = "smart-emergency-secret-key"

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "admin":
            return "Access Denied: Admin only", 403

        return f(*args, **kwargs)

    return decorated_function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                SELECT id, name, email, password, role
                FROM users
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()

            cursor.close()
            db.close()

            if user and check_password_hash(user[3], password):

                session["user_id"] = user[0]
                session["user_name"] = user[1]
                session["user_email"] = user[2]
                session["role"] = user[4]

                if user[4] == "admin":
                    return redirect("/dashboard")
                else:
                    return redirect("/")

            return render_template(
                "login.html",
                error="Invalid email or password"
            )

        except mysql.connector.Error as error:

            return render_template(
                "login.html",
                error=f"Database error: {error}"
            )

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
@app.route("/")
def home():
    try:
        db = get_db_connection()

        cursor = db.cursor()
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]

        cursor.close()
        db.close()

        return render_template(
            "index.html",
            database_name=database_name
        )

    except mysql.connector.Error as error:
        return f"Database connection error: {error}"
@app.route("/report", methods=["GET", "POST"])
@login_required
def report_emergency():

    if request.method == "POST":

        emergency_type = request.form["emergency_type"]
        description = request.form["description"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        priority = request.form["priority"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO emergencies
            (user_id, emergency_type, description,
             latitude, longitude, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"],
            emergency_type,
            description,
            latitude,
            longitude,
            priority
        ))

        db.commit()

        cursor.close()
        db.close()

        return """
        <h1>🚨 Emergency Reported Successfully</h1>
        <p>Your emergency has been recorded in the system.</p>
        <a href="/">Back to Home</a>
        """

    return render_template("report.html")
@app.route("/dashboard")
@admin_required
def dashboard():

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                emergency_type,
                description,
                latitude,
                longitude,
                priority,
                status,
                reported_at
            FROM emergencies
            ORDER BY reported_at DESC
        """)

        emergencies = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "dashboard.html",
            emergencies=emergencies
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/update_status/<int:emergency_id>/<status>")
@admin_required
def update_status(emergency_id, status):

    allowed_statuses = [
        "Reported",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:
        return "Invalid status", 400

    try:

        db = get_db_connection()
        cursor = db.cursor()


        # ==========================================
        # UPDATE EMERGENCY STATUS
        # ==========================================

        cursor.execute("""
            UPDATE emergencies
            SET status = %s
            WHERE id = %s
        """, (
            status,
            emergency_id
        ))


        # ==========================================
        # IF EMERGENCY IS RESOLVED
        # MAKE ASSIGNED VOLUNTEER AVAILABLE
        # ==========================================

        if status == "Resolved":

            cursor.execute("""
                UPDATE volunteers v
                JOIN emergency_assignments ea
                    ON v.id = ea.volunteer_id
                SET v.availability = 'Available'
                WHERE ea.emergency_id = %s
            """, (
                emergency_id,
            ))


        # ==========================================
        # SAVE CHANGES
        # ==========================================

        db.commit()


        cursor.close()
        db.close()


        return redirect("/dashboard")


    except mysql.connector.Error as error:

        return f"Database error: {error}"


@app.route("/emergency/<int:emergency_id>")
@admin_required
def emergency_details(emergency_id):

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Get emergency
        cursor.execute("""
            SELECT
                id,
                user_id,
                emergency_type,
                description,
                latitude,
                longitude,
                priority,
                status,
                reported_at
            FROM emergencies
            WHERE id = %s
        """, (emergency_id,))

        emergency = cursor.fetchone()

        if emergency is None:
            cursor.close()
            db.close()
            return "Emergency not found", 404

        # Get available resources
        cursor.execute("""
            SELECT
                id,
                name,
                resource_type,
                quantity,
                location,
                status
            FROM resources
            WHERE status = 'Available'
              AND quantity > 0
            ORDER BY name
        """)

        resources = cursor.fetchall()
                # Get available volunteers
        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                skills
            FROM volunteers
            WHERE availability = 'Available'
            ORDER BY name
        """)

        available_volunteers = cursor.fetchall()

        # Get volunteer already assigned to this emergency
        cursor.execute("""
            SELECT
                v.id,
                v.name,
                v.email,
                v.phone,
                v.skills,
                v.availability,
                ea.assigned_at
            FROM emergency_assignments ea
            JOIN volunteers v
                ON ea.volunteer_id = v.id
            WHERE ea.emergency_id = %s
            ORDER BY ea.assigned_at DESC
            LIMIT 1
        """, (emergency_id,))

        assigned_volunteer = cursor.fetchone()

        # Get resources already assigned to this emergency
        cursor.execute("""
            SELECT
                ra.id,
                r.name,
                r.resource_type,
                ra.quantity,
                ra.assigned_at,
                ra.released_at
            FROM resource_assignments ra
            JOIN resources r
                ON ra.resource_id = r.id
            WHERE ra.emergency_id = %s
            ORDER BY ra.assigned_at DESC
        """, (emergency_id,))

        assigned_resources = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "emergency_details.html",
            emergency=emergency,
            resources=resources,
            assigned_resources=assigned_resources,
            available_volunteers=available_volunteers,
            assigned_volunteer=assigned_volunteer
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/emergency/<int:emergency_id>/assign-resource", methods=["POST"])
@admin_required
def assign_resource(emergency_id):

    try:
        resource_id = request.form["resource_id"]
        quantity = int(request.form["quantity"])

        db = get_db_connection()
        cursor = db.cursor()

        # Check resource
        cursor.execute("""
            SELECT quantity, status
            FROM resources
            WHERE id = %s
        """, (resource_id,))

        resource = cursor.fetchone()

        if resource is None:
            cursor.close()
            db.close()
            return "Resource not found", 404

        available_quantity = resource[0]
        resource_status = resource[1]

        # Validate quantity
        if quantity <= 0:
            cursor.close()
            db.close()
            return "Invalid quantity", 400

        if quantity > available_quantity:
            cursor.close()
            db.close()
            return "Not enough resource quantity available", 400

        if resource_status != "Available":
            cursor.close()
            db.close()
            return "Resource is not available", 400

        # Create assignment
        cursor.execute("""
            INSERT INTO resource_assignments
            (emergency_id, resource_id, quantity)
            VALUES (%s, %s, %s)
        """, (
            emergency_id,
            resource_id,
            quantity
        ))

        # Update resource
        cursor.execute("""
            UPDATE resources
            SET quantity = quantity - %s,
                status = 'In Use'
            WHERE id = %s
        """, (
            quantity,
            resource_id
        ))

        db.commit()

        cursor.close()
        db.close()

        return redirect(
            f"/emergency/{emergency_id}"
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"

    except ValueError:
        return "Invalid quantity", 400


@app.route("/resources")
@admin_required
def resources():

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                resource_type,
                quantity,
                location,
                latitude,
                longitude,
                status,
                created_at
            FROM resources
            ORDER BY created_at DESC
        """)

        resources = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "resources.html",
            resources=resources
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"

@app.route("/resources/add", methods=["GET", "POST"])
@admin_required
def add_resource():
    if request.method == "POST":
        name = request.form["name"]
        resource_type = request.form["resource_type"]
        quantity = request.form["quantity"]
        location = request.form["location"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        status = request.form["status"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO resources
            (name, resource_type, quantity, location,
             latitude, longitude, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            resource_type,
            quantity,
            location,
            latitude,
            longitude,
            status
        ))

        db.commit()
        cursor.close()
        db.close()

        return redirect("/resources")

    return render_template("add_resource.html")
@app.route("/resource_status/<int:resource_id>/<status>")
@admin_required
def resource_status(resource_id, status):

    allowed_statuses = ["Available", "In Use", "Maintenance"]

    if status not in allowed_statuses:
        return "Invalid resource status", 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE resources
            SET status = %s
            WHERE id = %s
        """, (status, resource_id))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/resources")

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/resource-assignment/<int:assignment_id>/release", methods=["POST"])
@admin_required
def release_resource(assignment_id):

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Get assignment details
        cursor.execute("""
            SELECT resource_id, quantity
            FROM resource_assignments
            WHERE id = %s
              AND released_at IS NULL
        """, (assignment_id,))

        assignment = cursor.fetchone()

        if assignment is None:
            cursor.close()
            db.close()
            return "Assignment not found or resource already released", 404

        resource_id = assignment[0]
        assigned_quantity = assignment[1]

        # Mark assignment as released
        cursor.execute("""
            UPDATE resource_assignments
            SET released_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (assignment_id,))

        # Return quantity to resource
        cursor.execute("""
            UPDATE resources
            SET quantity = quantity + %s,
                status = 'Available'
            WHERE id = %s
        """, (assigned_quantity, resource_id))

        db.commit()

        cursor.close()
        db.close()

        return redirect(request.referrer or "/dashboard")

    except mysql.connector.Error as error:

        if 'db' in locals():
            db.rollback()

        return f"Database error: {error}"
@app.route("/my_emergencies")
@login_required
def my_emergencies():

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                e.id,
                e.emergency_type,
                e.description,
                e.priority,
                e.status,
                e.reported_at,
                v.name,
                v.email,
                v.phone,
                ea.assigned_at
            FROM emergencies e

            LEFT JOIN emergency_assignments ea
                ON ea.id = (
                    SELECT MAX(ea2.id)
                    FROM emergency_assignments ea2
                    WHERE ea2.emergency_id = e.id
                )

            LEFT JOIN volunteers v
                ON ea.volunteer_id = v.id

            WHERE e.user_id = %s

            ORDER BY e.reported_at DESC
        """, (session["user_id"],))

        emergencies = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "my_emergencies.html",
            emergencies=emergencies
        )

    except mysql.connector.Error as error:

        return f"Database error: {error}"
@app.route("/volunteers")
@admin_required
def volunteers():

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                skills,
                availability
            FROM volunteers
            ORDER BY id DESC
        """)

        volunteers = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "volunteers.html",
            volunteers=volunteers
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/volunteers/add", methods=["GET", "POST"])
@admin_required
def add_volunteer():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone")
        skills = request.form.get("skills")
        availability = request.form.get("availability", "Available")

        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO volunteers
                (name, email, phone, skills, availability)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                email,
                phone,
                skills,
                availability
            ))

            db.commit()

            cursor.close()
            db.close()

            return redirect("/volunteers")

        except mysql.connector.Error as error:
            return f"Database error: {error}"

    return render_template("add_volunteer.html")
@app.route("/volunteers/edit/<int:volunteer_id>", methods=["GET", "POST"])
@admin_required
def edit_volunteer(volunteer_id):

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == "POST":

            name = request.form["name"]
            email = request.form["email"]
            phone = request.form.get("phone")
            skills = request.form.get("skills")
            availability = request.form.get("availability", "Available")

            cursor.execute("""
                UPDATE volunteers
                SET name=%s,
                    email=%s,
                    phone=%s,
                    skills=%s,
                    availability=%s
                WHERE id=%s
            """, (
                name,
                email,
                phone,
                skills,
                availability,
                volunteer_id
            ))

            db.commit()

            cursor.close()
            db.close()

            return redirect("/volunteers")

        cursor.execute("""
            SELECT id, name, email, phone, skills, availability
            FROM volunteers
            WHERE id=%s
        """, (volunteer_id,))

        volunteer = cursor.fetchone()

        cursor.close()
        db.close()

        if not volunteer:
            return "Volunteer not found", 404

        return render_template(
            "edit_volunteer.html",
            volunteer=volunteer
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/volunteers/delete/<int:volunteer_id>", methods=["POST"])
@admin_required
def delete_volunteer(volunteer_id):

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            DELETE FROM volunteers
            WHERE id=%s
        """, (volunteer_id,))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/volunteers")

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/emergency/<int:emergency_id>/assign-volunteer", methods=["POST"])
@admin_required
def assign_volunteer(emergency_id):

    volunteer_id = request.form.get("volunteer_id")

    if not volunteer_id:
        return "Please select a volunteer", 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Check whether volunteer exists and is available
        cursor.execute("""
            SELECT id, availability
            FROM volunteers
            WHERE id = %s
        """, (volunteer_id,))

        volunteer = cursor.fetchone()

        if not volunteer:
            cursor.close()
            db.close()
            return "Volunteer not found", 404

        if volunteer[1] != "Available":
            cursor.close()
            db.close()
            return "Selected volunteer is not available", 400

        # Create assignment
        cursor.execute("""
            INSERT INTO emergency_assignments
            (emergency_id, volunteer_id)
            VALUES (%s, %s)
        """, (
            emergency_id,
            volunteer_id
        ))

        # Mark volunteer busy
        cursor.execute("""
            UPDATE volunteers
            SET availability = 'Busy'
            WHERE id = %s
        """, (volunteer_id,))

        db.commit()

        cursor.close()
        db.close()

        return redirect(
            f"/emergency/{emergency_id}"
        )

    except mysql.connector.Error as error:
        return f"Database error: {error}"
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            db = get_db_connection()
            cursor = db.cursor()

            # Check whether email already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                cursor.close()
                db.close()

                return render_template(
                    "register.html",
                    error="Email already registered"
                )

            # Hash password
            hashed_password = generate_password_hash(password)

            # Save user
            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, "student")
            )

            db.commit()

            cursor.close()
            db.close()

            return redirect("/login")

        except mysql.connector.Error as error:

            return render_template(
                "register.html",
                error=f"Database error: {error}"
            )

    return render_template("register.html")
if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )