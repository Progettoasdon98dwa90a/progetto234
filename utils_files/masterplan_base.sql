-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 17, 2025 at 11:32 AM
-- Server version: 8.0.40-0ubuntu0.22.04.1
-- PHP Version: 8.1.2-1ubuntu2.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `masterplan`
--

-- --------------------------------------------------------

--
-- Table structure for table `Absence`
--

CREATE TABLE `Absence` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `absent_type_id` int NOT NULL,
  `submitted` date DEFAULT NULL,
  `start` date NOT NULL,
  `end` date NOT NULL,
  `start_time` text,
  `end_time` text,
  `comment` text NOT NULL,
  `approved1` bit(1) NOT NULL DEFAULT b'0',
  `approved2` bit(1) NOT NULL DEFAULT b'0',
  `approved1_by_user_id` int DEFAULT NULL,
  `approved2_by_user_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `AbsentType`
--

CREATE TABLE `AbsentType` (
  `id` int NOT NULL,
  `shortname` text NOT NULL,
  `title` text NOT NULL,
  `color` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `AbsentType`
--

INSERT INTO `AbsentType` (`id`, `shortname`, `title`, `color`) VALUES
(1, '1111111', '1111111111', 'ffffff');

-- --------------------------------------------------------

--
-- Table structure for table `Holiday`
--

CREATE TABLE `Holiday` (
  `id` int NOT NULL,
  `title` text NOT NULL,
  `day` date NOT NULL,
  `service_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `PlannedService`
--

CREATE TABLE `PlannedService` (
  `id` int NOT NULL,
  `day` date NOT NULL,
  `service_id` int NOT NULL,
  `user_id` int NOT NULL,
  `icsmail_sent` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `PlannedServiceFile`
--

CREATE TABLE `PlannedServiceFile` (
  `id` int NOT NULL,
  `day` text NOT NULL,
  `service_id` int NOT NULL,
  `title` text NOT NULL,
  `file` longblob NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `PlannedServiceNote`
--

CREATE TABLE `PlannedServiceNote` (
  `id` int NOT NULL,
  `day` text NOT NULL,
  `service_id` int NOT NULL,
  `note` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `PlannedServiceResource`
--

CREATE TABLE `PlannedServiceResource` (
  `id` int NOT NULL,
  `day` text NOT NULL,
  `service_id` int NOT NULL,
  `resource_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `ReleasedPlan`
--

CREATE TABLE `ReleasedPlan` (
  `id` int NOT NULL,
  `roster_id` int NOT NULL,
  `day` date NOT NULL,
  `note` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Resource`
--

CREATE TABLE `Resource` (
  `id` int NOT NULL,
  `type` text NOT NULL,
  `title` text NOT NULL,
  `description` text NOT NULL,
  `icon` text NOT NULL,
  `color` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Role`
--

CREATE TABLE `Role` (
  `id` int NOT NULL,
  `title` text NOT NULL,
  `max_hours_per_day` int NOT NULL DEFAULT '-1',
  `max_services_per_week` int NOT NULL DEFAULT '-1',
  `max_hours_per_week` int NOT NULL DEFAULT '-1',
  `max_hours_per_month` int NOT NULL DEFAULT '-1'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Roster`
--

CREATE TABLE `Roster` (
  `id` int NOT NULL,
  `title` text NOT NULL,
  `autoplan_logic` int NOT NULL DEFAULT '0',
  `ignore_working_hours` bit(1) NOT NULL DEFAULT b'0',
  `icsmail_sender_name` text NOT NULL,
  `icsmail_sender_address` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Service`
--

CREATE TABLE `Service` (
  `id` int NOT NULL,
  `roster_id` int NOT NULL,
  `shortname` text NOT NULL,
  `title` text NOT NULL,
  `location` text NOT NULL,
  `employees` int NOT NULL,
  `start` text NOT NULL,
  `end` text NOT NULL,
  `date_start` text NOT NULL,
  `date_end` text NOT NULL,
  `color` text NOT NULL,
  `wd1` bit(1) NOT NULL DEFAULT b'0',
  `wd2` bit(1) NOT NULL DEFAULT b'0',
  `wd3` bit(1) NOT NULL DEFAULT b'0',
  `wd4` bit(1) NOT NULL DEFAULT b'0',
  `wd5` bit(1) NOT NULL DEFAULT b'0',
  `wd6` bit(1) NOT NULL DEFAULT b'0',
  `wd7` bit(1) NOT NULL DEFAULT b'0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Setting`
--

CREATE TABLE `Setting` (
  `setting` varchar(50) NOT NULL,
  `value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Setting`
--

INSERT INTO `Setting` (`setting`, `value`) VALUES
('rest_period', '13');

-- --------------------------------------------------------

--
-- Table structure for table `SwapService`
--

CREATE TABLE `SwapService` (
  `id` int NOT NULL,
  `planned_service_id` int NOT NULL,
  `comment` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE `User` (
  `id` int NOT NULL,
  `superadmin` int NOT NULL,
  `login` text NOT NULL,
  `firstname` text NOT NULL,
  `lastname` text NOT NULL,
  `fullname` text NOT NULL,
  `email` text,
  `phone` text,
  `mobile` text,
  `birthday` date DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `id_no` text,
  `description` text,
  `password` text,
  `ldap` bit(1) NOT NULL DEFAULT b'0',
  `locked` bit(1) NOT NULL DEFAULT b'0',
  `max_hours_per_day` int NOT NULL DEFAULT '0',
  `max_services_per_week` int NOT NULL DEFAULT '0',
  `max_hours_per_week` int NOT NULL DEFAULT '0',
  `max_hours_per_month` int NOT NULL DEFAULT '0',
  `color` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `User`
--

INSERT INTO `User` (`id`, `superadmin`, `login`, `firstname`, `lastname`, `fullname`, `email`, `phone`, `mobile`, `birthday`, `start_date`, `id_no`, `description`, `password`, `ldap`, `locked`, `max_hours_per_day`, `max_services_per_week`, `max_hours_per_week`, `max_hours_per_month`, `color`) VALUES
(1, 1, 'root', '', '', 'Administrator', '', '', '', NULL, '2025-01-17', '', 'initial admin user', '$2y$10$jpmFztn0QBl/fryspUFTAOmXZf86dzERCVvzNf8G4fGW1a4aa3cEW', b'0', b'0', -1, -1, -1, -1, '#fff');

-- --------------------------------------------------------

--
-- Table structure for table `UserConstraint`
--

CREATE TABLE `UserConstraint` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `service_id` int DEFAULT NULL,
  `wd1` bit(1) NOT NULL DEFAULT b'1',
  `wd2` bit(1) NOT NULL DEFAULT b'1',
  `wd3` bit(1) NOT NULL DEFAULT b'1',
  `wd4` bit(1) NOT NULL DEFAULT b'1',
  `wd5` bit(1) NOT NULL DEFAULT b'1',
  `wd6` bit(1) NOT NULL DEFAULT b'1',
  `wd7` bit(1) NOT NULL DEFAULT b'1',
  `comment` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `UserToRole`
--

CREATE TABLE `UserToRole` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `role_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `UserToRoster`
--

CREATE TABLE `UserToRoster` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `roster_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `UserToRosterAdmin`
--

CREATE TABLE `UserToRosterAdmin` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `roster_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Absence`
--
ALTER TABLE `Absence`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `absent_type_id` (`absent_type_id`),
  ADD KEY `fk_approve1user_absence` (`approved1_by_user_id`),
  ADD KEY `fk_approve2user_absence` (`approved2_by_user_id`);

--
-- Indexes for table `AbsentType`
--
ALTER TABLE `AbsentType`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Holiday`
--
ALTER TABLE `Holiday`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_service_10` (`service_id`);

--
-- Indexes for table `PlannedService`
--
ALTER TABLE `PlannedService`
  ADD PRIMARY KEY (`id`),
  ADD KEY `service_id` (`service_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `PlannedServiceFile`
--
ALTER TABLE `PlannedServiceFile`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_service4` (`service_id`);

--
-- Indexes for table `PlannedServiceNote`
--
ALTER TABLE `PlannedServiceNote`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_service3` (`service_id`);

--
-- Indexes for table `PlannedServiceResource`
--
ALTER TABLE `PlannedServiceResource`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_service5` (`service_id`),
  ADD KEY `fk_resource` (`resource_id`);

--
-- Indexes for table `ReleasedPlan`
--
ALTER TABLE `ReleasedPlan`
  ADD PRIMARY KEY (`id`),
  ADD KEY `roster_id` (`roster_id`);

--
-- Indexes for table `Resource`
--
ALTER TABLE `Resource`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Role`
--
ALTER TABLE `Role`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Roster`
--
ALTER TABLE `Roster`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Service`
--
ALTER TABLE `Service`
  ADD PRIMARY KEY (`id`),
  ADD KEY `roster_id` (`roster_id`);

--
-- Indexes for table `Setting`
--
ALTER TABLE `Setting`
  ADD PRIMARY KEY (`setting`);

--
-- Indexes for table `SwapService`
--
ALTER TABLE `SwapService`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `planned_service_id_2` (`planned_service_id`),
  ADD KEY `planned_service_id` (`planned_service_id`);

--
-- Indexes for table `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `UserConstraint`
--
ALTER TABLE `UserConstraint`
  ADD PRIMARY KEY (`id`),
  ADD KEY `service_id` (`service_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `UserToRole`
--
ALTER TABLE `UserToRole`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_role` (`role_id`),
  ADD KEY `fk_user4` (`user_id`);

--
-- Indexes for table `UserToRoster`
--
ALTER TABLE `UserToRoster`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `roster_id` (`roster_id`);

--
-- Indexes for table `UserToRosterAdmin`
--
ALTER TABLE `UserToRosterAdmin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `roster_id` (`roster_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Absence`
--
ALTER TABLE `Absence`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `AbsentType`
--
ALTER TABLE `AbsentType`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `Holiday`
--
ALTER TABLE `Holiday`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PlannedService`
--
ALTER TABLE `PlannedService`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PlannedServiceFile`
--
ALTER TABLE `PlannedServiceFile`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PlannedServiceNote`
--
ALTER TABLE `PlannedServiceNote`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PlannedServiceResource`
--
ALTER TABLE `PlannedServiceResource`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ReleasedPlan`
--
ALTER TABLE `ReleasedPlan`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Resource`
--
ALTER TABLE `Resource`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Role`
--
ALTER TABLE `Role`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Roster`
--
ALTER TABLE `Roster`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Service`
--
ALTER TABLE `Service`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `SwapService`
--
ALTER TABLE `SwapService`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `UserConstraint`
--
ALTER TABLE `UserConstraint`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `UserToRole`
--
ALTER TABLE `UserToRole`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `UserToRoster`
--
ALTER TABLE `UserToRoster`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `UserToRosterAdmin`
--
ALTER TABLE `UserToRosterAdmin`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Absence`
--
ALTER TABLE `Absence`
  ADD CONSTRAINT `fk_approve1user_absence` FOREIGN KEY (`approved1_by_user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_approve2user_absence` FOREIGN KEY (`approved2_by_user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_type_absence` FOREIGN KEY (`absent_type_id`) REFERENCES `AbsentType` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user_absence` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `Holiday`
--
ALTER TABLE `Holiday`
  ADD CONSTRAINT `fk_service_10` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `PlannedService`
--
ALTER TABLE `PlannedService`
  ADD CONSTRAINT `fk_service2` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user3` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `PlannedServiceFile`
--
ALTER TABLE `PlannedServiceFile`
  ADD CONSTRAINT `fk_service4` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`);

--
-- Constraints for table `PlannedServiceNote`
--
ALTER TABLE `PlannedServiceNote`
  ADD CONSTRAINT `fk_service3` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `PlannedServiceResource`
--
ALTER TABLE `PlannedServiceResource`
  ADD CONSTRAINT `fk_resource` FOREIGN KEY (`resource_id`) REFERENCES `Resource` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_service5` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `ReleasedPlan`
--
ALTER TABLE `ReleasedPlan`
  ADD CONSTRAINT `fk_roster_releasedplan` FOREIGN KEY (`roster_id`) REFERENCES `Roster` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `Service`
--
ALTER TABLE `Service`
  ADD CONSTRAINT `fk_roster2` FOREIGN KEY (`roster_id`) REFERENCES `Roster` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `SwapService`
--
ALTER TABLE `SwapService`
  ADD CONSTRAINT `fk_planned_service_swap` FOREIGN KEY (`planned_service_id`) REFERENCES `PlannedService` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `UserConstraint`
--
ALTER TABLE `UserConstraint`
  ADD CONSTRAINT `fk_service` FOREIGN KEY (`service_id`) REFERENCES `Service` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `UserToRole`
--
ALTER TABLE `UserToRole`
  ADD CONSTRAINT `fk_role` FOREIGN KEY (`role_id`) REFERENCES `Role` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user4` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `UserToRoster`
--
ALTER TABLE `UserToRoster`
  ADD CONSTRAINT `fk_roster` FOREIGN KEY (`roster_id`) REFERENCES `Roster` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user2` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `UserToRosterAdmin`
--
ALTER TABLE `UserToRosterAdmin`
  ADD CONSTRAINT `fk_roster_rosteradmin` FOREIGN KEY (`roster_id`) REFERENCES `Roster` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user_rosteradmin` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
