CREATE SCHEMA IF NOT EXISTS `elementary`;
USE `elementary` ;

-- -----------------------------------------------------
-- Table `elementary`.`post_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post_type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_UNIQUE` (`name`))
ENGINE = InnoDB;

INSERT INTO `elementary`.`post_type` (`name`) VALUES
  ('notice'),
  ('parent_letter'),
  ('school_meal');


-- -----------------------------------------------------
-- Table `elementary`.`post`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elementary`.`post` (
  `id` INT NOT NULL,
  `author` VARCHAR(30) NOT NULL,
  `upload_at` DATE NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `content` MEDIUMTEXT NULL,
  `post_type_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_post_post_type1`
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
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attached_file_UNIQUE` (`attached_file_id`,`file_sn`),
  CONSTRAINT `fk_attached_file_post`
    FOREIGN KEY (`post_id`)
    REFERENCES `elementary`.`post` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;
