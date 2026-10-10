-- MySQL Schema matching original avmsdb.sql
CREATE TABLE IF NOT EXISTS `tbladmin` (
  `ID` int(5) NOT NULL AUTO_INCREMENT,
  `AdminName` varchar(45) DEFAULT NULL,
  `UserName` varchar(45) UNIQUE DEFAULT NULL,
  `MobileNumber` bigint(11) DEFAULT NULL,
  `Email` varchar(120) DEFAULT NULL,
  `Password` varchar(120) DEFAULT NULL,
  `AdminRegdate` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tblcategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `categoryName` varchar(120) DEFAULT NULL,
  `creationDate` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tblvisitor` (
  `ID` int(5) NOT NULL AUTO_INCREMENT,
  `categoryName` varchar(120) DEFAULT NULL,
  `VisitorName` varchar(120) DEFAULT NULL,
  `MobileNumber` bigint(11) DEFAULT NULL,
  `Address` varchar(250) DEFAULT NULL,
  `Apartment` varchar(120) NOT NULL,
  `Floor` varchar(120) NOT NULL,
  `WhomtoMeet` varchar(120) DEFAULT NULL,
  `ReasontoMeet` varchar(120) DEFAULT NULL,
  `EnterDate` timestamp NULL DEFAULT current_timestamp(),
  `remark` varchar(255) DEFAULT NULL,
  `outtime` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (`ID`),
  KEY `idx_visitor_enterdate` (`EnterDate`),
  KEY `idx_visitor_mobile` (`MobileNumber`),
  KEY `idx_visitor_name` (`VisitorName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `tblvisitorpass` (
  `ID` int(5) NOT NULL AUTO_INCREMENT,
  `passnumber` bigint(20) DEFAULT NULL,
  `categoryName` varchar(120) DEFAULT NULL,
  `VisitorName` varchar(120) DEFAULT NULL,
  `MobileNumber` bigint(11) DEFAULT NULL,
  `Address` varchar(250) DEFAULT NULL,
  `Apartment` varchar(120) NOT NULL,
  `Floor` varchar(120) NOT NULL,
  `passDetails` varchar(120) DEFAULT NULL,
  `creationDate` timestamp NULL DEFAULT current_timestamp(),
  `fromDate` date DEFAULT NULL,
  `toDate` date NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `idx_pass_creationdate` (`creationDate`),
  KEY `idx_pass_number` (`passnumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
