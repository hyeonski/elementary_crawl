CREATE SCHEMA IF NOT EXISTS `elementary`;
USE `elementary` ;

-- -----------------------------------------------------
-- Table `elementary`.`post_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post_type` (
  `id` INT NOT NULL,
  `name` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE (`name`))
ENGINE = InnoDB;

INSERT INTO `elementary`.`post_type` (`id`, `name`) VALUES
  (1, 'notice'),
  (2, 'parent_letter'),
  (3, 'school_meal'),
  (4, 'school_meal_menu');

-- -----------------------------------------------------
-- Table `elementary`.`post`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `data_key` VARCHAR(20) NOT NULL,
  `post_type_id` INT NOT NULL,
  `author` VARCHAR(30) NOT NULL,
  `upload_at` DATE NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `content` MEDIUMTEXT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`),
  UNIQUE (`data_key`),
  FOREIGN KEY (`post_type_id`)
  REFERENCES `elementary`.`post_type` (`id`)
  ON DELETE RESTRICT
  ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `elementary`.`attached_file`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`attached_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `post_id` INT NOT NULL,
  `attached_file_id` VARCHAR(30) NOT NULL,
  `file_sn` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `size` INT UNSIGNED NOT NULL,
  `preview_url` VARCHAR(255) NOT NULL,
  `download_url` VARCHAR(255) NOT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attached_file_UNIQUE` (`attached_file_id`,`file_sn`),
  FOREIGN KEY (`post_id`)
  REFERENCES `elementary`.`post` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE)
ENGINE = InnoDB;
