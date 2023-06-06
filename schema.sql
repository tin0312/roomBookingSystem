
----------------------- Organized Tables ----------------------------

-- show create table reservation;
CREATE TABLE `reservation` (
  `reservation_id` int NOT NULL AUTO_INCREMENT,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `date` date NOT NULL,
  `roomNo` varchar(10) NOT NULL,
  `occupancy` int NOT NULL,
  `username` int unsigned NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'Booked',
  `adminID` int unsigned DEFAULT NULL,
  PRIMARY KEY (`reservation_id`),
  KEY `roomNo` (`roomNo`),
  KEY `username` (`username`),
  CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`roomNo`) REFERENCES `room` (`roomNo`) ON UPDATE CASCADE,
  CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`username`) REFERENCES `useraccount` (`username`) ON UPDATE CASCADE
);
-- show create table room; 
CREATE TABLE `room` (
  `roomNo` varchar(10) NOT NULL,
  `roomType` varchar(10) NOT NULL,
  `maxReservationDuration` int NOT NULL,
  PRIMARY KEY (`roomNo`)
)

insert into room values ('LIB202A', 'study', 3);
insert into room values ('LIB202B', 'digital', 3);
insert into room values ('LIB202C', 'carrel', 3);
insert into room values ('LIB303', 'study', 4);
insert into room values ('LIB304', 'digital', 4);
insert into room values ('LIB305', 'carrel', 4);
insert into room values ('LIB306', 'study', 4);
insert into room values ('LIB307', 'digital', 4);
insert into room values ('LIB309', 'carrel', 4);
insert into room values ('LIB310', 'study', 4);

-- show create table roomtype;
CREATE TABLE `roomtype` (
  `roomType` varchar(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`roomType`)
)
insert into roomtype values ('study', 'Group Study Room');
insert into roomtype values ('digital', 'Digital Media Lab');
insert into roomtype values ('carrel', 'Assited Carrel');

-- show create table useraccount;
CREATE TABLE `useraccount` (
  `username` int unsigned NOT NULL,
  `password` varchar(255) NOT NULL,
  `status` enum('Student','Teaching Faculty') DEFAULT NULL,
  `firstname` varchar(25) NOT NULL,
  `lastname` varchar(25) NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`username`)
  UNIQUE (email),
  CONSTRAINT legalname UNIQUE (firstname, lastname, username));

INSERT INTO useraccount VALUES
(100809801, MD5('1234test'), 'Teaching Faculty', 'Richard W.','Pazzi','Richard.pazzi@uoit.ca'),
(100858194, MD5('1234test'), 'Student', 'Wajiha', 'Zaheer','wajiha.zaheer@ontariotechu.com'),
(100709100, MD5('1234test'), 'Student', 'Nhat Truong','Hoang','nhattruong.hoang@ontariotechu.com'),
(123456789, MD5('1234test'), 'Student', 'fTest','lTest','fTest.lTest@ontariotechu.com'),
(100809811, MD5('1234test'), 'Teaching Faculty', 'fTTest','lTTest','lTTest.fTTest@uoit.ca');

-- show create table adminaccount;
CREATE TABLE `adminaccount` (
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `firstname` varchar(25) NOT NULL,
  `lastname` varchar(25) NOT NULL,
  `email` varchar(255) NOT NULL,
  UNIQUE KEY `username` (`username`)
  UNIQUE (email),
  CONSTRAINT legalname UNIQUE (firstname, lastname, username));

INSERT INTO adminaccount (username, password, firstname, lastname, email) VALUES
 ('admWzaheer', MD5('admin123'), 'Admin', 'admWzaheer', 'admWzaheer@ontariotechu.com'),
 ('admNhoang', MD5('admin123'), 'Admin', 'admNhoang', 'admnhattruong.hoang@ontariotechu.com'),
 ('admRwpazzi', MD5('admin123'), 'Admin', 'admRwpazzi', 'admRwpazzi@ontariotechu.com'),
 ('admTest', MD5('admin123'), 'Admin', 'admTest', 'admTest@ontariotechu.com');

-- show create table student;
CREATE TABLE `student` (
  `firstname` varchar(25) NOT NULL,
  `lastname` varchar(25) NOT NULL,
  `username` int unsigned NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `legalname` (`firstname`,`lastname`),
  CONSTRAINT `fk_student_useraccount` FOREIGN KEY (`username`) REFERENCES `useraccount` (`username`) ON UPDATE CASCADE
)
-- show create table faculty; 
CREATE TABLE `faculty` (
  `firstname` varchar(25) NOT NULL,
  `lastname` varchar(25) NOT NULL,
  `username` int unsigned NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `legalname` (`firstname`,`lastname`),
  CONSTRAINT `fk_faculty_useraccount` FOREIGN KEY (`username`) REFERENCES `useraccount` (`username`) ON UPDATE CASCADE
)

 