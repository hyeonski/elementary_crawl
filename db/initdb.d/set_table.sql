CREATE SCHEMA IF NOT EXISTS `elementary`;
USE `elementary` ;

-- -----------------------------------------------------
-- Table `elementary`.`post`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post` (
  `id` INT NOT NULL,
  `post_type` VARCHAR(30) NOT NULL,
  `author` VARCHAR(30) NOT NULL,
  `upload_at` DATE NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `content` MEDIUMTEXT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`))
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
  CONSTRAINT `fk_attached_file_post`
    FOREIGN KEY (`post_id`)
    REFERENCES `elementary`.`post` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `elementary`.`school_meal_menu`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`school_meal_menu` (
  `id` INT NOT NULL,
  `type` VARCHAR(30) NOT NULL,
  `upload_at` DATE NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `menu` VARCHAR(100) NOT NULL,
  `image_url` VARCHAR(255) NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
