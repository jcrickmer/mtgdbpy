-- MySQL dump 10.13  Distrib 5.1.71, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: mtgdb
-- ------------------------------------------------------
-- Server version	5.1.71

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `basecards`
--

DROP TABLE IF EXISTS `basecards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `basecards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `rules_text` varchar(1000) DEFAULT NULL,
  `mana_cost` varchar(60) NOT NULL DEFAULT '',
  `cmc` smallint(6) NOT NULL DEFAULT '0',
  `power` char(4) DEFAULT NULL,
  `toughness` char(4) DEFAULT NULL,
  `loyalty` char(4) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2380 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cardcolors`
--

DROP TABLE IF EXISTS `cardcolors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cardcolors` (
  `basecard_id` int(11) NOT NULL,
  `color_id` char(1) NOT NULL,
  PRIMARY KEY (`basecard_id`,`color_id`),
  KEY `color_id` (`color_id`),
  CONSTRAINT `cardcolors_ibfk_1` FOREIGN KEY (`basecard_id`) REFERENCES `basecards` (`id`),
  CONSTRAINT `cardcolors_ibfk_2` FOREIGN KEY (`color_id`) REFERENCES `colors` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cards`
--

DROP TABLE IF EXISTS `cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cards` (
  `expansionset_id` int(11) NOT NULL DEFAULT '0',
  `basecard_id` int(11) NOT NULL DEFAULT '0',
  `rarity` char(1) DEFAULT NULL,
  `multiverseid` int(11) DEFAULT NULL,
  `flavor_text` varchar(1000) DEFAULT NULL,
  `card_number` int(11) DEFAULT NULL,
  `mark_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`expansionset_id`,`basecard_id`),
  UNIQUE KEY `multiverseid` (`multiverseid`),
  UNIQUE KEY `expansionset_id` (`expansionset_id`,`card_number`),
  KEY `basecard_id` (`basecard_id`),
  KEY `rarity` (`rarity`),
  KEY `mark_id` (`mark_id`),
  CONSTRAINT `cards_ibfk_1` FOREIGN KEY (`basecard_id`) REFERENCES `basecards` (`id`),
  CONSTRAINT `cards_ibfk_2` FOREIGN KEY (`expansionset_id`) REFERENCES `expansionsets` (`id`),
  CONSTRAINT `cards_ibfk_3` FOREIGN KEY (`rarity`) REFERENCES `rarities` (`id`),
  CONSTRAINT `cards_ibfk_4` FOREIGN KEY (`mark_id`) REFERENCES `marks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cardsubtypes`
--

DROP TABLE IF EXISTS `cardsubtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cardsubtypes` (
  `basecard_id` int(11) NOT NULL,
  `subtype_id` int(11) NOT NULL,
  `position` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`basecard_id`,`subtype_id`,`position`),
  KEY `subtype_id` (`subtype_id`),
  CONSTRAINT `cardsubtypes_ibfk_1` FOREIGN KEY (`basecard_id`) REFERENCES `basecards` (`id`),
  CONSTRAINT `cardsubtypes_ibfk_2` FOREIGN KEY (`subtype_id`) REFERENCES `subtypes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cardtypes`
--

DROP TABLE IF EXISTS `cardtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cardtypes` (
  `basecard_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `position` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`basecard_id`,`type_id`,`position`),
  KEY `type_id` (`type_id`),
  CONSTRAINT `cardtypes_ibfk_1` FOREIGN KEY (`basecard_id`) REFERENCES `basecards` (`id`),
  CONSTRAINT `cardtypes_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `colors`
--

DROP TABLE IF EXISTS `colors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `colors` (
  `id` char(1) NOT NULL,
  `color` char(9) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expansionsets`
--

DROP TABLE IF EXISTS `expansionsets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expansionsets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `abbr` char(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `abbr` (`abbr`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marks`
--

DROP TABLE IF EXISTS `marks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mark` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rarities`
--

DROP TABLE IF EXISTS `rarities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rarities` (
  `id` char(1) NOT NULL,
  `rarity` char(11) NOT NULL,
  `sortorder` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subtypes`
--

DROP TABLE IF EXISTS `subtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subtypes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subtype` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=294 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `types`
--

DROP TABLE IF EXISTS `types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-01-02 19:14:35
