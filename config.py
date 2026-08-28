import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "16936")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),

    # Aiven MySQL SSL
    "ssl_disabled": False,
    "ssl_verify_cert": False,
    "ssl_verify_identity": False
}