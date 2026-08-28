-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: smart_emergency_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `emergencies`
--

DROP TABLE IF EXISTS `emergencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emergencies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `emergency_type` enum('Medical','Fire','Accident','Security','Other') NOT NULL,
  `description` text,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `priority` enum('Low','Medium','High','Critical') DEFAULT 'Medium',
  `status` enum('Reported','Assigned','In Progress','Resolved') DEFAULT 'Reported',
  `reported_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `emergencies_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emergencies`
--

LOCK TABLES `emergencies` WRITE;
/*!40000 ALTER TABLE `emergencies` DISABLE KEYS */;
INSERT INTO `emergencies` VALUES (1,1,'Fire','fire',19.20000000,20.90000000,'Medium','Resolved','2026-08-12 10:27:54'),(2,1,'Other','help there are 4 people in the building 2 under the wall',-2.00000000,6.00000000,'High','Resolved','2026-08-12 11:14:02'),(3,1,'Security','heilp need',14.00000000,60.00000000,'Medium','Resolved','2026-08-16 07:49:51'),(4,1,'Fire','help me',10.00000000,7.00000000,'Medium','Resolved','2026-08-19 12:47:17'),(5,1,'Accident','a bus get accident with tree',19.07483600,72.87294700,'Medium','Resolved','2026-08-23 15:55:10');
/*!40000 ALTER TABLE `emergencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emergency_assignments`
--

DROP TABLE IF EXISTS `emergency_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emergency_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `emergency_id` int NOT NULL,
  `volunteer_id` int DEFAULT NULL,
  `resource_id` int DEFAULT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `emergency_id` (`emergency_id`),
  KEY `volunteer_id` (`volunteer_id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `emergency_assignments_ibfk_1` FOREIGN KEY (`emergency_id`) REFERENCES `emergencies` (`id`),
  CONSTRAINT `emergency_assignments_ibfk_2` FOREIGN KEY (`volunteer_id`) REFERENCES `volunteers` (`id`),
  CONSTRAINT `emergency_assignments_ibfk_3` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emergency_assignments`
--

LOCK TABLES `emergency_assignments` WRITE;
/*!40000 ALTER TABLE `emergency_assignments` DISABLE KEYS */;
INSERT INTO `emergency_assignments` VALUES (1,4,2,NULL,'2026-08-22 08:33:43'),(2,5,3,NULL,'2026-08-23 15:57:15');
/*!40000 ALTER TABLE `emergency_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emergency_logs`
--

DROP TABLE IF EXISTS `emergency_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emergency_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `emergency_id` int NOT NULL,
  `status` varchar(50) NOT NULL,
  `note` text,
  `updated_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `emergency_id` (`emergency_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `emergency_logs_ibfk_1` FOREIGN KEY (`emergency_id`) REFERENCES `emergencies` (`id`),
  CONSTRAINT `emergency_logs_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emergency_logs`
--

LOCK TABLES `emergency_logs` WRITE;
/*!40000 ALTER TABLE `emergency_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `emergency_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_assignments`
--

DROP TABLE IF EXISTS `resource_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `emergency_id` int NOT NULL,
  `resource_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `released_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `emergency_id` (`emergency_id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `resource_assignments_ibfk_1` FOREIGN KEY (`emergency_id`) REFERENCES `emergencies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resource_assignments_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_assignments`
--

LOCK TABLES `resource_assignments` WRITE;
/*!40000 ALTER TABLE `resource_assignments` DISABLE KEYS */;
INSERT INTO `resource_assignments` VALUES (1,1,3,1,'2026-08-15 10:34:31','2026-08-16 07:43:52'),(2,1,2,1,'2026-08-15 10:44:17','2026-08-15 10:45:42'),(3,1,2,1,'2026-08-16 07:43:33','2026-08-16 07:44:57'),(4,1,4,2,'2026-08-16 07:44:13','2026-08-16 07:44:42'),(5,3,4,1,'2026-08-19 12:46:12','2026-08-19 12:46:22'),(6,4,3,1,'2026-08-22 08:34:01','2026-08-22 08:52:05'),(7,5,5,1,'2026-08-23 15:57:31','2026-08-23 16:03:09');
/*!40000 ALTER TABLE `resource_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resources`
--

DROP TABLE IF EXISTS `resources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `resource_type` varchar(100) NOT NULL,
  `quantity` int DEFAULT '0',
  `location` varchar(255) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `status` enum('Available','In Use','Maintenance') DEFAULT 'Available',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resources`
--

LOCK TABLES `resources` WRITE;
/*!40000 ALTER TABLE `resources` DISABLE KEYS */;
INSERT INTO `resources` VALUES (1,'Campus Ambulance','Medical',1,'Main Gate',19.20000000,20.90000000,'In Use','2026-08-13 13:04:55'),(2,'First Aid Kit','Medical Equipment',10,'Main Building',19.20100000,20.90100000,'Available','2026-08-13 11:56:16'),(3,'Fire Extinguisher','Fire Safety',8,'Computer Lab',19.20200000,20.90200000,'Available','2026-08-13 11:56:16'),(4,'Security Team','Security',5,'Campus Gate',19.20300000,20.90300000,'Available','2026-08-13 11:56:16'),(5,'Rescue Team','Rescue',3,'Admin Building',19.20400000,20.90400000,'Available','2026-08-13 11:56:16');
/*!40000 ALTER TABLE `resources` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','staff','admin') DEFAULT 'student',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Demo Student','demo@student.com','demo123','student','2026-08-11 14:10:09'),(2,'System Admin','admin@smartemergency.com','admin123','admin','2026-08-18 14:08:56'),(3,'Rahul Sharma','rahul@student.com','rahul123','student','2026-08-19 12:55:48'),(4,'Priya Staff','priya@smartemergency.com','priya123','staff','2026-08-19 12:55:48'),(5,'Emergency Admin','admin2@smartemergency.com','admin123','admin','2026-08-19 12:55:48');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `volunteers`
--

DROP TABLE IF EXISTS `volunteers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `volunteers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `skills` varchar(255) DEFAULT NULL,
  `availability` enum('Available','Busy','Unavailable') DEFAULT 'Available',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `volunteers`
--

LOCK TABLES `volunteers` WRITE;
/*!40000 ALTER TABLE `volunteers` DISABLE KEYS */;
INSERT INTO `volunteers` VALUES (1,'Amit Sharma','amit@smartemergency.com','9876543210','First Aid, Medical Support','Available','2026-08-19 13:06:33'),(2,'Neha Verma','neha@smartemergency.com','9876543211','Fire Safety, Rescue','Available','2026-08-19 13:06:33'),(3,'Rohit Patil','rohit@smartemergency.com','9876543212','Security, Crowd Control','Available','2026-08-19 13:06:33'),(4,'Priya Singh','priya.volunteer@smartemergency.com','9876543213','First Aid, Communication','Busy','2026-08-19 13:06:33'),(5,'Karan Yadav','karan@smartemergency.com','9876543214','Rescue, Evacuation','Available','2026-08-19 13:06:33'),(7,'KRISHNA YADAV','kRISHNA@smartemergency.com','8097574923','First Aid','Available','2026-08-21 12:28:11');
/*!40000 ALTER TABLE `volunteers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-25 20:10:22
