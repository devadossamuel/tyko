-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 15, 2019 at 12:25 PM
-- Server version: 10.1.38-MariaDB
-- PHP Version: 7.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jsharrs_av_preservation`
--

-- --------------------------------------------------------

--
-- Table structure for table `audio_video`
--

CREATE TABLE `audio_video` (
  `item_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `date_recorded` date DEFAULT NULL,
  `side` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `format_subtype` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `playback_notes` longtext COLLATE utf8_unicode_ci,
  `inspection_notes` longtext COLLATE utf8_unicode_ci,
  `treatment_needed` longtext COLLATE utf8_unicode_ci,
  `treatment_given` longtext COLLATE utf8_unicode_ci,
  `staff_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `collection`
--

CREATE TABLE `collection` (
  `collection_id` int(11) NOT NULL,
  `record_series` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `collection_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `department` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `col_contact_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `collection_contact`
--

CREATE TABLE `collection_contact` (
  `col_contact_id` int(11) NOT NULL,
  `first_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email_address` varchar(100) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `film`
--

CREATE TABLE `film` (
  `item_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `date_of_film` date DEFAULT NULL,
  `can_label` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `leader_label` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `duration` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  `format_guage` int(11) DEFAULT NULL,
  `base` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `edge_code_date` date DEFAULT NULL,
  `sound` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `color` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `image_type` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `AD_test_date` date DEFAULT NULL,
  `AD_test_level` int(11) DEFAULT NULL,
  `inspection_notes` longtext COLLATE utf8_unicode_ci,
  `other_notes` longtext COLLATE utf8_unicode_ci,
  `treatment_needed` longtext COLLATE utf8_unicode_ci,
  `treatment_given` longtext COLLATE utf8_unicode_ci,
  `treatment_date` date DEFAULT NULL,
  `staff_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `format`
--

CREATE TABLE `format` (
  `format_id` int(11) NOT NULL,
  `format_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `grooved_disc`
--

CREATE TABLE `grooved_disc` (
  `item_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `date_recorded` year(4) DEFAULT NULL,
  `side` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `diameter` int(11) DEFAULT NULL,
  `disc_material` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `base` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `playback_direction` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `playback_speed` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `notes` longtext COLLATE utf8_unicode_ci,
  `inspection_notes` longtext COLLATE utf8_unicode_ci,
  `treatment_needed` longtext COLLATE utf8_unicode_ci,
  `treatment_given` longtext COLLATE utf8_unicode_ci,
  `staff_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `item`
--

CREATE TABLE `item` (
  `item_id` int(11) NOT NULL,
  `item_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `barcode` int(11) DEFAULT NULL,
  `file_name` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `medusa_uuid` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `originals_rec_date` date NOT NULL,
  `originals_return_date` date DEFAULT NULL,
  `object_id` int(11) DEFAULT NULL,
  `item_obj_sequence` int(11) DEFAULT NULL,
  `collection_id` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `object`
--

CREATE TABLE `object` (
  `object_id` int(11) NOT NULL,
  `object_name` varchar(250) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `open_reel`
--

CREATE TABLE `open_reel` (
  `item_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `date_recorded` date DEFAULT NULL,
  `track_count` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `tape_size` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reel_diam` int(11) DEFAULT NULL,
  `reel_type` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `tape_thickness` int(11) DEFAULT NULL,
  `tape_brand` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `base` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `wind` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `tape_speed` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `track_config` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  `generation` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `playback_notes` longtext COLLATE utf8_unicode_ci,
  `inspection_notes` longtext COLLATE utf8_unicode_ci,
  `treatment_needed` longtext COLLATE utf8_unicode_ci,
  `treatment_given` longtext COLLATE utf8_unicode_ci,
  `staff_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `preservation_staff`
--

CREATE TABLE `preservation_staff` (
  `staff_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `first_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email_address` varchar(100) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `project`
--

CREATE TABLE `project` (
  `project_id` int(11) NOT NULL,
  `project_code` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `project_title` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `current_location` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `project_status` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `project_specs` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `project_notes` longtext COLLATE utf8_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendor`
--

CREATE TABLE `vendor` (
  `vendor_id` int(11) NOT NULL,
  `vendor_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `vendor_address` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `vendor_city` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `vendor_state` varchar(2) COLLATE utf8_unicode_ci NOT NULL,
  `vendor_zipcode` varchar(10) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendor_contact`
--

CREATE TABLE `vendor_contact` (
  `vendor_contact_id` int(11) NOT NULL,
  `first_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email_address` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `vendor_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendor_item_transfers`
--

CREATE TABLE `vendor_item_transfers` (
  `item_id` int(11) NOT NULL,
  `vendor_id` int(11) NOT NULL,
  `deliverables_rec_date` date DEFAULT NULL,
  `originals_rec_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `audio_video`
--
ALTER TABLE `audio_video`
  ADD PRIMARY KEY (`item_id`,`format_id`),
  ADD KEY `format_id` (`format_id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- Indexes for table `collection`
--
ALTER TABLE `collection`
  ADD PRIMARY KEY (`collection_id`),
  ADD KEY `col_contact_id` (`col_contact_id`);

--
-- Indexes for table `collection_contact`
--
ALTER TABLE `collection_contact`
  ADD PRIMARY KEY (`col_contact_id`);

--
-- Indexes for table `film`
--
ALTER TABLE `film`
  ADD PRIMARY KEY (`item_id`,`format_id`),
  ADD KEY `format_id` (`format_id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- Indexes for table `format`
--
ALTER TABLE `format`
  ADD PRIMARY KEY (`format_id`);

--
-- Indexes for table `grooved_disc`
--
ALTER TABLE `grooved_disc`
  ADD PRIMARY KEY (`item_id`,`format_id`),
  ADD KEY `format_id` (`format_id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- Indexes for table `item`
--
ALTER TABLE `item`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `collection_id` (`collection_id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `object_id` (`object_id`);

--
-- Indexes for table `object`
--
ALTER TABLE `object`
  ADD PRIMARY KEY (`object_id`);

--
-- Indexes for table `open_reel`
--
ALTER TABLE `open_reel`
  ADD PRIMARY KEY (`item_id`,`format_id`),
  ADD KEY `format_id` (`format_id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- Indexes for table `preservation_staff`
--
ALTER TABLE `preservation_staff`
  ADD PRIMARY KEY (`staff_id`);

--
-- Indexes for table `project`
--
ALTER TABLE `project`
  ADD PRIMARY KEY (`project_id`);

--
-- Indexes for table `vendor`
--
ALTER TABLE `vendor`
  ADD PRIMARY KEY (`vendor_id`);

--
-- Indexes for table `vendor_contact`
--
ALTER TABLE `vendor_contact`
  ADD PRIMARY KEY (`vendor_contact_id`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- Indexes for table `vendor_item_transfers`
--
ALTER TABLE `vendor_item_transfers`
  ADD PRIMARY KEY (`item_id`,`vendor_id`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `collection`
--
ALTER TABLE `collection`
  MODIFY `collection_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `collection_contact`
--
ALTER TABLE `collection_contact`
  MODIFY `col_contact_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `format`
--
ALTER TABLE `format`
  MODIFY `format_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `item`
--
ALTER TABLE `item`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `object`
--
ALTER TABLE `object`
  MODIFY `object_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `project`
--
ALTER TABLE `project`
  MODIFY `project_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `vendor`
--
ALTER TABLE `vendor`
  MODIFY `vendor_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `audio_video`
--
ALTER TABLE `audio_video`
  ADD CONSTRAINT `audio_video_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`),
  ADD CONSTRAINT `audio_video_ibfk_2` FOREIGN KEY (`format_id`) REFERENCES `format` (`format_id`),
  ADD CONSTRAINT `audio_video_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `preservation_staff` (`staff_id`);

--
-- Constraints for table `collection`
--
ALTER TABLE `collection`
  ADD CONSTRAINT `collection_ibfk_1` FOREIGN KEY (`col_contact_id`) REFERENCES `collection_contact` (`col_contact_id`);

--
-- Constraints for table `film`
--
ALTER TABLE `film`
  ADD CONSTRAINT `film_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`),
  ADD CONSTRAINT `film_ibfk_2` FOREIGN KEY (`format_id`) REFERENCES `format` (`format_id`),
  ADD CONSTRAINT `film_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `preservation_staff` (`staff_id`);

--
-- Constraints for table `grooved_disc`
--
ALTER TABLE `grooved_disc`
  ADD CONSTRAINT `grooved_disc_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`),
  ADD CONSTRAINT `grooved_disc_ibfk_2` FOREIGN KEY (`format_id`) REFERENCES `format` (`format_id`),
  ADD CONSTRAINT `grooved_disc_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `preservation_staff` (`staff_id`);

--
-- Constraints for table `item`
--
ALTER TABLE `item`
  ADD CONSTRAINT `item_ibfk_1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`collection_id`),
  ADD CONSTRAINT `item_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project` (`project_id`),
  ADD CONSTRAINT `item_ibfk_3` FOREIGN KEY (`object_id`) REFERENCES `object` (`object_id`);

--
-- Constraints for table `open_reel`
--
ALTER TABLE `open_reel`
  ADD CONSTRAINT `open_reel_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`),
  ADD CONSTRAINT `open_reel_ibfk_2` FOREIGN KEY (`format_id`) REFERENCES `format` (`format_id`),
  ADD CONSTRAINT `open_reel_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `preservation_staff` (`staff_id`);

--
-- Constraints for table `vendor_contact`
--
ALTER TABLE `vendor_contact`
  ADD CONSTRAINT `vendor_contact_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendor` (`vendor_id`);

--
-- Constraints for table `vendor_item_transfers`
--
ALTER TABLE `vendor_item_transfers`
  ADD CONSTRAINT `vendor_item_transfers_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`),
  ADD CONSTRAINT `vendor_item_transfers_ibfk_2` FOREIGN KEY (`vendor_id`) REFERENCES `vendor` (`vendor_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
