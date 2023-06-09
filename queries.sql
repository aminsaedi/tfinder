SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `twitter`;
CREATE DATABASE `twitter` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `twitter`;

DROP TABLE IF EXISTS `search`;
CREATE TABLE `search` (
  `id` varchar(255) COLLATE utf8mb3_bin NOT NULL,
  `posted_at` datetime NOT NULL,
  `screen_name` varchar(255) COLLATE utf8mb3_bin NOT NULL,
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;