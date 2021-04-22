-- MySQL Script generated by MySQL Workbench
-- Mon Apr 12 21:27:02 2021
-- Model: New Model  Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema gradebook
-- -----------------------------------------------------
-- Gradebook schema for IS668 project

-- -----------------------------------------------------
-- Schema gradebook
--
-- Gradebook schema for IS668 project
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS gradebook DEFAULT CHARACTER SET utf8 ;
USE gradebook ;

-- -----------------------------------------------------
-- Table  student
-- -----------------------------------------------------
DROP TABLE IF EXISTS  student ;

CREATE TABLE IF NOT EXISTS student (
  student_ID INT NOT NULL COMMENT 'Artificial primary key.',
  first_name VARCHAR(45) NOT NULL COMMENT 'The first name of the student.',
  last_name VARCHAR(45) NOT NULL COMMENT 'The last name of the student.',
  email_address VARCHAR(45) NULL COMMENT 'The email address of the student.',
  major VARCHAR(45) NULL COMMENT 'The school major of the student.',
 PRIMARY KEY ( student_ID ))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table  course
-- -----------------------------------------------------
/*
DROP TABLE IF EXISTS course ;

CREATE TABLE IF NOT EXISTS course (
  course_ID INT NOT NULL,
  course_name VARCHAR(45) NOT NULL COMMENT 'The name of the school class.',
 PRIMARY KEY ( course_ID ))
ENGINE = InnoDB;
*/
-- -----------------------------------------------------
-- Table  enrollment
-- -----------------------------------------------------
/*
DROP TABLE IF EXISTS  course_offering;

CREATE TABLE IF NOT EXISTS  course_offering (
  offering_ID INT NOT NULL COMMENT 'Artificial primary key',
  course_ID INT NOT NULL COMMENT 'Foreign key from course table. Composite primary key.',
  course_year INT,
  semester VARCHAR(45),
  PRIMARY KEY(offering_ID),
  CONSTRAINT course_constraint
  FOREIGN KEY(course_ID)
  REFERENCES course(course_ID)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION)
ENGINE = InnoDB;
*/
-- -----------------------------------------------------
-- Table  enrollment
-- -----------------------------------------------------
/*
DROP TABLE IF EXISTS  enrollment;

CREATE TABLE IF NOT EXISTS  enrollment (
  student_ID INT NOT NULL COMMENT 'Foreign key from student table. Composite primary key.',
  offering_ID INT NOT NULL COMMENT 'Foreign key from course_offering table. Composite primary key.',
  PRIMARY KEY(student_ID, offering_ID),
  CONSTRAINT student_enrollment_constraint
  FOREIGN KEY(student_ID)
  REFERENCES student(student_ID)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
 CONSTRAINT offering_ID_constraint
  FOREIGN KEY(offering_ID)
  REFERENCES course_offering(offering_ID)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION)
ENGINE = InnoDB;
*/
-- -----------------------------------------------------
-- Table  assignment
-- -----------------------------------------------------
DROP TABLE IF EXISTS assignment;

CREATE TABLE IF NOT EXISTS assignment (
  assignment_ID INT NOT NULL COMMENT 'Artificial primary key.',
  assignment_name VARCHAR(45) NULL COMMENT 'The name of the assignment.',
  -- offering_ID INT NOT NULL COMMENT 'Foreign key from schoolClass table.',
 PRIMARY KEY (assignment_ID)) -- ,
 -- CONSTRAINT enrollment_assignment_constraint
  -- FOREIGN KEY(offering_ID)
  -- REFERENCES course_offering(offering_ID)
  -- ON DELETE NO ACTION
  -- ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table  grade
-- -----------------------------------------------------
DROP TABLE IF EXISTS  grade ;

CREATE TABLE IF NOT EXISTS  grade (
  assignment_ID INT NOT NULL COMMENT 'Foreign key from assignment table. Part of composite primary key.',
  student_ID INT NOT NULL COMMENT 'Foreign key from student table. Part of composite primary key.',
  grade FLOAT NULL COMMENT 'Stores a student grade for an assignment',
 PRIMARY KEY (assignment_ID, student_ID),
 CONSTRAINT assignment_grade_constraint
  FOREIGN KEY(assignment_ID)
  REFERENCES  assignment(assignment_ID)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
 CONSTRAINT student_grade_constraint
  FOREIGN KEY(student_ID)
  REFERENCES student(student_ID)
  ON DELETE CASCADE
  ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
