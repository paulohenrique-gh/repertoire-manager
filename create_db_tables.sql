CREATE DATABASE music_pieces;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `hash` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `periods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
);

CREATE TABLE `composers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `period_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  FOREIGN KEY (`period_id`) REFERENCES `periods` (`id`)
);

CREATE TABLE `instruments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
);

CREATE TABLE `pieces` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(100) NOT NULL,
  `opus` int DEFAULT NULL,
  `number_in_opus` int DEFAULT NULL,
  `movement` int DEFAULT NULL,
  `composer_id` int NOT NULL,
  `instrument_id` int DEFAULT NULL,
  `difficulty_level` int DEFAULT NULL,
  `is_in_repertoire` tinyint(1) NOT NULL,
  `start_date` date DEFAULT NULL,
  `finish_date` date DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  FOREIGN KEY (`instrument_id`) REFERENCES `instruments` (`id`),
  FOREIGN KEY (`composer_id`) REFERENCES `composers` (`id`)
);

CREATE TABLE `calendar` (
  `date_to_play` date NOT NULL,
  `piece_id` int NOT NULL
);