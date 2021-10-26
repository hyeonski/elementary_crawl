CREATE SCHEMA IF NOT EXISTS `elementary`;
USE `elementary` ;

-- -----------------------------------------------------
-- Table `elementary`.`post_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post_type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE (`name`))
ENGINE = InnoDB;

INSERT INTO `elementary`.`post_type` (`name`) VALUES
  ('공지사항'),
  ('가정통신문'),
  ('급식 소식'),
  ('오늘의 급식');

-- -----------------------------------------------------
-- Table `elementary`.`school`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`school` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE (`name`))
ENGINE = InnoDB;

INSERT INTO `elementary`.`school` (`name`) VALUES
  ('서울서이초등학교');

-- -----------------------------------------------------
-- Table `elementary`.`post`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `school_id` INT NOT NULL,
  `post_type_id` INT NOT NULL,
  `data_key` VARCHAR(20) NOT NULL,
  `author` VARCHAR(30) NOT NULL,
  `upload_at` DATE NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `content` MEDIUMTEXT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`),
  UNIQUE (`school_id`, `post_type_id`, `data_key`),
  FOREIGN KEY (`post_type_id`)
  REFERENCES `elementary`.`post_type` (`id`)
  ON DELETE RESTRICT
  ON UPDATE CASCADE,
  FOREIGN KEY (`school_id`)
  REFERENCES `elementary`.`school` (`id`)
  ON DELETE RESTRICT
  ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `elementary`.`attached_file`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`attached_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `post_id` INT NOT NULL,
  `data_key` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `size` INT UNSIGNED NOT NULL,
  `download_url` VARCHAR(255) NOT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`),
  UNIQUE (`post_id`, `data_key`),
  FOREIGN KEY (`post_id`)
  REFERENCES `elementary`.`post` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE)
ENGINE = InnoDB;
