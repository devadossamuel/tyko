-- MariaDB dump 10.17  Distrib 10.4.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: av_preservation
-- ------------------------------------------------------
-- Server version	10.4.7-MariaDB-1:10.4.7+maria~bionic

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audio_video`
--

DROP TABLE IF EXISTS `audio_video`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audio_video` (
  `item_id` int(11) NOT NULL,
  `date_recorded` date DEFAULT NULL,
  `side` text DEFAULT NULL,
  `duration` text DEFAULT NULL,
  `format_subtype` text DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  CONSTRAINT `audio_video_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audio_video`
--

LOCK TABLES `audio_video` WRITE;
/*!40000 ALTER TABLE `audio_video` DISABLE KEYS */;
/*!40000 ALTER TABLE `audio_video` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collection`
--

DROP TABLE IF EXISTS `collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection` (
  `collection_id` int(11) NOT NULL AUTO_INCREMENT,
  `record_series` text DEFAULT NULL,
  `collection_name` text DEFAULT NULL,
  `department` text DEFAULT NULL,
  `contact_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`collection_id`),
  KEY `contact_id` (`contact_id`),
  CONSTRAINT `collection_ibfk_1` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collection`
--

LOCK TABLES `collection` WRITE;
/*!40000 ALTER TABLE `collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact`
--

DROP TABLE IF EXISTS `contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contact` (
  `contact_id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` text DEFAULT NULL,
  `last_name` text DEFAULT NULL,
  `email_address` text DEFAULT NULL,
  PRIMARY KEY (`contact_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact`
--

LOCK TABLES `contact` WRITE;
/*!40000 ALTER TABLE `contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `film`
--

DROP TABLE IF EXISTS `film`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `film` (
  `item_id` int(11) NOT NULL,
  `date_of_film` date DEFAULT NULL,
  `can_label` text DEFAULT NULL,
  `leader_label` text DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `duration` text DEFAULT NULL,
  `format_gauge` int(11) DEFAULT NULL,
  `base` text DEFAULT NULL,
  `edge_code_date` date DEFAULT NULL,
  `sound` text DEFAULT NULL,
  `color` text DEFAULT NULL,
  `image_type` text DEFAULT NULL,
  `ad_test_date` date DEFAULT NULL,
  `ad_test_level` int(11) DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  CONSTRAINT `film_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `film`
--

LOCK TABLES `film` WRITE;
/*!40000 ALTER TABLE `film` DISABLE KEYS */;
/*!40000 ALTER TABLE `film` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `format_types`
--

DROP TABLE IF EXISTS `format_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `format_types` (
  `format_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  PRIMARY KEY (`format_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `format_types`
--

LOCK TABLES `format_types` WRITE;
/*!40000 ALTER TABLE `format_types` DISABLE KEYS */;
INSERT INTO `format_types` VALUES (1,'audio video'),(2,'audio'),(3,'video'),(4,'open reel'),(5,'grooved disc'),(6,'film');
/*!40000 ALTER TABLE `format_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grooved_disc`
--

DROP TABLE IF EXISTS `grooved_disc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grooved_disc` (
  `item_id` int(11) NOT NULL,
  `date_recorded` int(11) DEFAULT NULL,
  `side` text DEFAULT NULL,
  `duration` text DEFAULT NULL,
  `diameter` int(11) DEFAULT NULL,
  `disc_material` text DEFAULT NULL,
  `base` text DEFAULT NULL,
  `playback_direction` text DEFAULT NULL,
  `playback_speed` text DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  CONSTRAINT `grooved_disc_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grooved_disc`
--

LOCK TABLES `grooved_disc` WRITE;
/*!40000 ALTER TABLE `grooved_disc` DISABLE KEYS */;
/*!40000 ALTER TABLE `grooved_disc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `file_name` text DEFAULT NULL,
  `medusa_uuid` text DEFAULT NULL,
  `object_id` int(11) DEFAULT NULL,
  `obj_sequence` int(11) DEFAULT NULL,
  `format_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  KEY `object_id` (`object_id`),
  KEY `format_type_id` (`format_type_id`),
  CONSTRAINT `item_ibfk_1` FOREIGN KEY (`object_id`) REFERENCES `object` (`object_id`),
  CONSTRAINT `item_ibfk_2` FOREIGN KEY (`format_type_id`) REFERENCES `format_types` (`format_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_has_contacts`
--

DROP TABLE IF EXISTS `item_has_contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item_has_contacts` (
  `contact_id` int(11) DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  KEY `contact_id` (`contact_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `item_has_contacts_ibfk_1` FOREIGN KEY (`contact_id`) REFERENCES `item` (`item_id`),
  CONSTRAINT `item_has_contacts_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `contact` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_has_contacts`
--

LOCK TABLES `item_has_contacts` WRITE;
/*!40000 ALTER TABLE `item_has_contacts` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_has_contacts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_has_notes`
--

DROP TABLE IF EXISTS `item_has_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item_has_notes` (
  `notes_id` int(11) DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  KEY `notes_id` (`notes_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `item_has_notes_ibfk_1` FOREIGN KEY (`notes_id`) REFERENCES `notes` (`note_id`),
  CONSTRAINT `item_has_notes_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_has_notes`
--

LOCK TABLES `item_has_notes` WRITE;
/*!40000 ALTER TABLE `item_has_notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_has_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `note_types`
--

DROP TABLE IF EXISTS `note_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `note_types` (
  `note_types_id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` text DEFAULT NULL,
  PRIMARY KEY (`note_types_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `note_types`
--

LOCK TABLES `note_types` WRITE;
/*!40000 ALTER TABLE `note_types` DISABLE KEYS */;
INSERT INTO `note_types` VALUES (1,'Inspection'),(2,'Playback'),(3,'Project'),(4,'Other');
/*!40000 ALTER TABLE `note_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notes` (
  `note_id` int(11) NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `note_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`note_id`),
  KEY `note_type_id` (`note_type_id`),
  CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`note_type_id`) REFERENCES `note_types` (`note_types_id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `object`
--

DROP TABLE IF EXISTS `object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `object` (
  `object_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `barcode` text DEFAULT NULL,
  `collection_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `originals_rec_date` date DEFAULT NULL,
  `originals_return_date` date DEFAULT NULL,
  `contact_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`object_id`),
  KEY `collection_id` (`collection_id`),
  KEY `project_id` (`project_id`),
  KEY `contact_id` (`contact_id`),
  CONSTRAINT `object_ibfk_1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`collection_id`),
  CONSTRAINT `object_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`),
  CONSTRAINT `object_ibfk_3` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `object`
--

LOCK TABLES `object` WRITE;
/*!40000 ALTER TABLE `object` DISABLE KEYS */;
/*!40000 ALTER TABLE `object` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `object_has_notes`
--

DROP TABLE IF EXISTS `object_has_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `object_has_notes` (
  `notes_id` int(11) DEFAULT NULL,
  `object_id` int(11) DEFAULT NULL,
  KEY `notes_id` (`notes_id`),
  KEY `object_id` (`object_id`),
  CONSTRAINT `object_has_notes_ibfk_1` FOREIGN KEY (`notes_id`) REFERENCES `notes` (`note_id`),
  CONSTRAINT `object_has_notes_ibfk_2` FOREIGN KEY (`object_id`) REFERENCES `object` (`object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `object_has_notes`
--

LOCK TABLES `object_has_notes` WRITE;
/*!40000 ALTER TABLE `object_has_notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `object_has_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `open_reel`
--

DROP TABLE IF EXISTS `open_reel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `open_reel` (
  `item_id` int(11) NOT NULL,
  `date_recorded` date DEFAULT NULL,
  `track_count` text DEFAULT NULL,
  `tape_size` text DEFAULT NULL,
  `reel_diam` int(11) DEFAULT NULL,
  `reel_type` text DEFAULT NULL,
  `tape_thickness` int(11) DEFAULT NULL,
  `tape_brand` text DEFAULT NULL,
  `base` text DEFAULT NULL,
  `wind` text DEFAULT NULL,
  `track_speed` text DEFAULT NULL,
  `track_configuration` text DEFAULT NULL,
  `track_duration` text DEFAULT NULL,
  `generation` text DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  CONSTRAINT `open_reel_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `open_reel`
--

LOCK TABLES `open_reel` WRITE;
/*!40000 ALTER TABLE `open_reel` DISABLE KEYS */;
/*!40000 ALTER TABLE `open_reel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `project_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_code` text DEFAULT NULL,
  `title` text DEFAULT NULL,
  `current_location` text DEFAULT NULL,
  `status` text DEFAULT NULL,
  `specs` text DEFAULT NULL,
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_has_notes`
--

DROP TABLE IF EXISTS `project_has_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_has_notes` (
  `notes_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  KEY `notes_id` (`notes_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `project_has_notes_ibfk_1` FOREIGN KEY (`notes_id`) REFERENCES `notes` (`note_id`),
  CONSTRAINT `project_has_notes_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_has_notes`
--

LOCK TABLES `project_has_notes` WRITE;
/*!40000 ALTER TABLE `project_has_notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_has_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treatment`
--

DROP TABLE IF EXISTS `treatment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treatment` (
  `treatment_id` int(11) NOT NULL AUTO_INCREMENT,
  `needed` text DEFAULT NULL,
  `given` text DEFAULT NULL,
  `date` date DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`treatment_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
/*!40000 ALTER TABLE `treatment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor`
--

DROP TABLE IF EXISTS `vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendor` (
  `vendor_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` text DEFAULT NULL,
  `state` text DEFAULT NULL,
  `zipcode` text DEFAULT NULL,
  PRIMARY KEY (`vendor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor`
--

LOCK TABLES `vendor` WRITE;
/*!40000 ALTER TABLE `vendor` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor_has_contacts`
--

DROP TABLE IF EXISTS `vendor_has_contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendor_has_contacts` (
  `contact_id` int(11) DEFAULT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  KEY `contact_id` (`contact_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `vendor_has_contacts_ibfk_1` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`),
  CONSTRAINT `vendor_has_contacts_ibfk_2` FOREIGN KEY (`vendor_id`) REFERENCES `vendor` (`vendor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor_has_contacts`
--

LOCK TABLES `vendor_has_contacts` WRITE;
/*!40000 ALTER TABLE `vendor_has_contacts` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendor_has_contacts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor_transfer`
--

DROP TABLE IF EXISTS `vendor_transfer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendor_transfer` (
  `vendor_transfer_id` int(11) NOT NULL AUTO_INCREMENT,
  `vendor_id` int(11) DEFAULT NULL,
  `vendor_deliverables_rec_date` date DEFAULT NULL,
  `returned_originals_rec_date` date DEFAULT NULL,
  PRIMARY KEY (`vendor_transfer_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `vendor_transfer_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendor` (`vendor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor_transfer`
--

LOCK TABLES `vendor_transfer` WRITE;
/*!40000 ALTER TABLE `vendor_transfer` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendor_transfer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor_transfer_has_an_object`
--

DROP TABLE IF EXISTS `vendor_transfer_has_an_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendor_transfer_has_an_object` (
  `object_id` int(11) DEFAULT NULL,
  `vendor_transfer_id` int(11) DEFAULT NULL,
  KEY `object_id` (`object_id`),
  KEY `vendor_transfer_id` (`vendor_transfer_id`),
  CONSTRAINT `vendor_transfer_has_an_object_ibfk_1` FOREIGN KEY (`object_id`) REFERENCES `object` (`object_id`),
  CONSTRAINT `vendor_transfer_has_an_object_ibfk_2` FOREIGN KEY (`vendor_transfer_id`) REFERENCES `vendor_transfer` (`vendor_transfer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor_transfer_has_an_object`
--

LOCK TABLES `vendor_transfer_has_an_object` WRITE;
/*!40000 ALTER TABLE `vendor_transfer_has_an_object` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendor_transfer_has_an_object` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-09-30 21:14:17
