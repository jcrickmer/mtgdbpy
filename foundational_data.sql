--
-- Dumping data for table `colors`
--

LOCK TABLES `colors` WRITE;
/*!40000 ALTER TABLE `colors` DISABLE KEYS */;
INSERT INTO `colors` (`id`, `color`) VALUES ('B','Black');
INSERT INTO `colors` (`id`, `color`) VALUES ('c','Colorless');
INSERT INTO `colors` (`id`, `color`) VALUES ('G','Green');
INSERT INTO `colors` (`id`, `color`) VALUES ('R','Red');
INSERT INTO `colors` (`id`, `color`) VALUES ('U','Blue');
INSERT INTO `colors` (`id`, `color`) VALUES ('W','White');
/*!40000 ALTER TABLE `colors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `rarities`
--

LOCK TABLES `rarities` WRITE;
/*!40000 ALTER TABLE `rarities` DISABLE KEYS */;
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('b','Basic Land',NULL);
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('c','Common',0);
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('m','Mythic Rare',3);
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('s','Special',4);
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('r','Rare',2);
INSERT INTO `rarities` (`id`, `rarity`, `sortorder`) VALUES ('u','Uncommon',1);
/*!40000 ALTER TABLE `rarities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `marks`
--

LOCK TABLES `marks` WRITE;
/*!40000 ALTER TABLE `marks` DISABLE KEYS */;
INSERT INTO `marks` (`id`, `mark`) VALUES (1,'Azorius');
INSERT INTO `marks` (`id`, `mark`) VALUES (2,'Boros');
INSERT INTO `marks` (`id`, `mark`) VALUES (3,'Dimir');
INSERT INTO `marks` (`id`, `mark`) VALUES (4,'Golgari');
INSERT INTO `marks` (`id`, `mark`) VALUES (5,'Gruul');
INSERT INTO `marks` (`id`, `mark`) VALUES (6,'Izzet');
INSERT INTO `marks` (`id`, `mark`) VALUES (7,'Mirran');
INSERT INTO `marks` (`id`, `mark`) VALUES (8,'Orzhov');
INSERT INTO `marks` (`id`, `mark`) VALUES (9,'Phyrexian');
INSERT INTO `marks` (`id`, `mark`) VALUES (10,'Rakdos');
INSERT INTO `marks` (`id`, `mark`) VALUES (11,'Selesnya');
INSERT INTO `marks` (`id`, `mark`) VALUES (12,'Simic');
/*!40000 ALTER TABLE `marks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `expansionsets`
--

LOCK TABLES `expansionsets` WRITE;
/*!40000 ALTER TABLE `expansionsets` DISABLE KEYS */;
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (1,'2012 Holiday Gift Box','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (2,'Alara Reborn','ARB');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (3,'Alliances','ALL');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (4,'Anthologies','ATH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (5,'Antiquities','ATQ');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (6,'Apocalypse','APC');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (7,'Arabian Nights','ARN');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (8,'Archenemy','ARC');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (9,'Astral','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (10,'Avacyn Restored','AVR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (11,'Battle Royale Box Set','BRB');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (12,'Beatdown Box Set','BTD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (13,'Betrayers of Kamigawa','BOK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (14,'Born of the Gods','BNG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (15,'Champions of Kamigawa','CHK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (16,'Chronicles','CHR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (17,'Classic Sixth Edition','6ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (18,'Coldsnap','CSP');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (19,'Collector\'s Edition','CED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (20,'Magic: The Gathering - Commander','CMD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (21,'Commander 2013 Edition','C13');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (22,'Commander\'s Arsenal','CM1');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (23,'Conflux','CON');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (24,'Magic: The Gathering - Conspiracy','CNS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (25,'Eighth Edition','8ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (26,'Ninth Edition','9ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (27,'Tenth Edition','10E');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (28,'Dark Ascension','DKA');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (29,'Darksteel','DST');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (30,'Deck Builder\'s Toolkit','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (31,'Deck Builder\'s Toolkit (2012 Edition)','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (32,'Deck Builder\'s Toolkit (2014 Core Set Edition)','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (33,'Deck Builder\'s Toolkit (Refreshed Version)','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (34,'Deckmasters: Garfield vs. Finkel','DKM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (35,'Dissension','DIS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (36,'Dragon\'s Maze','DGM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (37,'Duel Decks: Ajani vs. Nicol Bolas','DDH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (38,'Duel Decks: Divine vs. Demonic','DDC');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (39,'Duel Decks: Elspeth vs. Tezzeret','DDF');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (40,'Duel Decks: Elves vs. Goblins','EVG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (41,'Duel Decks: Garruk vs. Liliana','DDD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (42,'Duel Decks: Heroes vs. Monsters','DDL');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (43,'Duel Decks: Izzet vs. Golgari','DDJ');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (44,'Duel Decks: Jace vs. Chandra','DD2');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (45,'Duel Decks: Jace vs. Vraska','DDM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (46,'Duel Decks: Knights vs. Dragons','DDG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (47,'Duel Decks: Phyrexia vs. the Coalition','DDE');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (48,'Duel Decks: Sorin vs. Tibalt','DDK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (49,'Duel Decks: Speed vs. Cunning','DDN');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (50,'Duel Decks: Venser vs. Koth','DDI');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (51,'Duels of the Planeswalkers (decks)','DPA');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (52,'Eventide','EVE');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (53,'Exodus','EXO');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (54,'Fallen Empires','FEM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (55,'Fifth Dawn','5DN');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (56,'Fifth Edition','5ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (57,'Fourth Edition','4ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (58,'From the Vault: Annihilation','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (59,'From the Vault: Dragons','DRB');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (60,'From the Vault: Exiled','V09');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (61,'From the Vault: Legends','V11');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (62,'From the Vault: Realms','V12');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (63,'From the Vault: Relics','V10');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (64,'From the Vault: Twenty','V13');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (65,'Future Sight','FUT');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (66,'Gatecrash','GTC');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (67,'Guildpact','GPT');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (68,'Homelands','HML');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (69,'Ice Age','ICE');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (70,'Innistrad','ISD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (71,'International Collector\'s Edition','CED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (72,'Invasion','INV');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (73,'Journey into Nyx','JOU');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (74,'Judgment','JUD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (75,'Khans of Tarkir','KTK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (76,'Legends','LEG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (77,'Legions','LGN');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (78,'Limited Edition Alpha','LEA');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (79,'Limited Edition Beta','LEB');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (80,'Lorwyn','LRW');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (81,'Magic 2010','M10');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (82,'Magic 2011','M11');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (83,'Magic 2012','M12');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (84,'Magic 2013','M13');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (85,'Magic 2014 Core Set','M14');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (86,'Magic 2015','M15');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (87,'Mercadian Masques','MMQ');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (88,'Mirage','MIR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (89,'Mirrodin','MRD');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (90,'Mirrodin Besieged','MBS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (91,'Modern Event Deck 2014','MD1');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (92,'Modern Masters','MMA');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (93,'Morningtide','MOR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (94,'Multiverse Gift Box','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (95,'Nemesis','NEM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (96,'New Phyrexia','NPH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (97,'Odyssey','ODY');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (98,'Onslaught','ONS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (99,'Planar Chaos','PLC');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (100,'Planechase','HOP');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (101,'Planechase 2012 Edition','PC2');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (102,'Planeshift','PLS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (103,'Portal','POR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (104,'Portal Second Age','PO2');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (105,'Portal Three Kingdoms','PTK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (106,'Premium Deck Series: Fire and Lightning','PD2');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (107,'Premium Deck Series: Graveborn','PD3');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (108,'Premium Deck Series: Slivers','H09');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (109,'Premium Foil Booster','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (110,'Prophecy','PCY');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (111,'Ravnica: City of Guilds','RAV');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (112,'Return to Ravnica','RTR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (113,'Revised Edition','3ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (114,'Rise of the Eldrazi','ROE');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (115,'Rivals Quick Start Set','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (116,'Saviors of Kamigawa','SOK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (117,'Scars of Mirrodin','SOM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (118,'Scourge','SCG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (119,'Seventh Edition','7ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (120,'Shadowmoor','SHM');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (121,'Shards of Alara','ALA');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (122,'Starter 1999','S99');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (123,'Starter 2000','S00');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (124,'Stronghold','STH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (125,'Tempest','TMP');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (126,'The Dark','DRK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (127,'Theros','THS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (128,'Time Spiral','TSP');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (129,'Torment','TOR');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (130,'Unglued','UGL');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (131,'Unhinged','UNH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (132,'Unlimited Edition','2ED');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (133,'Urza\'s Destiny','UDS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (134,'Urza\'s Legacy','ULG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (135,'Urza\'s Saga','USG');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (136,'Visions','VIS');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (137,'Weatherlight','WTH');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (138,'Worldwake','WWK');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (139,'Zendikar','ZEN');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (140,'Masters Edition IV','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (141,'Time Spiral \"Timeshifted\"','TSB');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (142,'Masters Edition II','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (143,'Masters Edition','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (144,'Masters Edition III','');
INSERT INTO `expansionsets` (`id`, `name`, `abbr`) VALUES (145,'Promo set for Gatherer','');
/*!40000 ALTER TABLE `expansionsets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `types`
--

LOCK TABLES `types` WRITE;
/*!40000 ALTER TABLE `types` DISABLE KEYS */;
INSERT INTO `types` (`id`, `type`) VALUES (1,'Artifact');
INSERT INTO `types` (`id`, `type`) VALUES (2,'Basic');
INSERT INTO `types` (`id`, `type`) VALUES (3,'Creature');
INSERT INTO `types` (`id`, `type`) VALUES (4,'Enchantment');
INSERT INTO `types` (`id`, `type`) VALUES (5,'Instant');
INSERT INTO `types` (`id`, `type`) VALUES (6,'Land');
INSERT INTO `types` (`id`, `type`) VALUES (7,'Legendary');
INSERT INTO `types` (`id`, `type`) VALUES (8,'Ongoing');
INSERT INTO `types` (`id`, `type`) VALUES (9,'Phenomenon');
INSERT INTO `types` (`id`, `type`) VALUES (10,'Plane');
INSERT INTO `types` (`id`, `type`) VALUES (11,'Planeswalker');
INSERT INTO `types` (`id`, `type`) VALUES (12,'Scheme');
INSERT INTO `types` (`id`, `type`) VALUES (13,'Snow');
INSERT INTO `types` (`id`, `type`) VALUES (14,'Sorcery');
INSERT INTO `types` (`id`, `type`) VALUES (15,'Tribal');
INSERT INTO `types` (`id`, `type`) VALUES (16,'Vanguard');
INSERT INTO `types` (`id`, `type`) VALUES (17,'World');
/*!40000 ALTER TABLE `types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `subtypes`
--

LOCK TABLES `subtypes` WRITE;
/*!40000 ALTER TABLE `subtypes` DISABLE KEYS */;
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (1,'Advisor');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (2,'Ajani');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (3,'Alara');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (4,'Ally');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (5,'Angel');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (6,'Anteater');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (7,'Antelope');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (8,'Ape');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (9,'Arcane');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (10,'Archer');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (11,'Archon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (12,'Arkhos');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (13,'Artificer');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (14,'Assassin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (15,'Assembly-Worker');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (16,'Atog');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (17,'Aura');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (18,'Aurochs');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (19,'Avatar');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (20,'Azgol');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (21,'Badger');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (22,'Barbarian');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (23,'Basilisk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (24,'Bat');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (25,'Bear');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (26,'Beast');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (27,'Beeble');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (28,'Belenon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (29,'Berserker');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (30,'Bird');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (31,'Boar');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (32,'Bolas');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (33,'Bolas\'s');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (34,'Bringer');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (35,'Brushwagg');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (36,'Camel');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (37,'Carrier');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (38,'Cat');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (39,'Centaur');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (40,'Cephalid');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (41,'Chandra');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (42,'Chimera');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (43,'Cleric');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (44,'Cockatrice');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (45,'Construct');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (46,'Crab');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (47,'Crocodile');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (48,'Curse');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (49,'Cyclops');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (50,'Dauthi');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (51,'Demon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (52,'Desert');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (53,'Devil');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (54,'Djinn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (55,'Dominaria');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (56,'Domri');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (57,'Dragon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (58,'Drake');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (59,'Dreadnought');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (60,'Drone');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (61,'Druid');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (62,'Dryad');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (63,'Dwarf');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (64,'Efreet');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (65,'Egg');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (66,'Elder');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (67,'Eldrazi');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (68,'Elemental');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (69,'Elephant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (70,'Elf');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (71,'Elk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (72,'Elspeth');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (73,'Equilor');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (74,'Equipment');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (75,'Ergamon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (76,'Eye');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (77,'Fabacin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (78,'Faerie');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (79,'Ferret');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (80,'Fish');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (81,'Flagbearer');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (82,'Forest');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (83,'Fortification');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (84,'Fox');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (85,'Frog');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (86,'Fungus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (87,'Gargoyle');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (88,'Garruk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (89,'Gate');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (90,'Giant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (91,'Gideon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (92,'Gnome');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (93,'Goat');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (94,'Goblin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (95,'Golem');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (96,'Gorgon');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (97,'Gremlin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (98,'Griffin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (99,'Hag');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (100,'Harpy');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (101,'Hellion');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (102,'Hippo');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (103,'Hippogriff');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (104,'Homarid');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (105,'Homunculus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (106,'Horror');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (107,'Horse');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (108,'Hound');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (109,'Human');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (110,'Hydra');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (111,'Hyena');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (112,'Illusion');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (113,'Imp');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (114,'Incarnation');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (115,'Innistrad');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (116,'Insect');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (117,'Iquatana');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (118,'Ir');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (119,'Island');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (120,'Jace');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (121,'Jellyfish');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (122,'Juggernaut');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (123,'Kaldheim');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (124,'Kamigawa');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (125,'Karn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (126,'Kavu');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (127,'Kephalai');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (128,'Kirin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (129,'Kithkin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (130,'Knight');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (131,'Kobold');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (132,'Kolbahan');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (133,'Kor');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (134,'Koth');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (135,'Kraken');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (136,'Kyneth');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (137,'Lair');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (138,'Lammasu');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (139,'Leech');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (140,'Leviathan');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (141,'Lhurgoyf');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (142,'Licid');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (143,'Liliana');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (144,'Lizard');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (145,'Locus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (146,'Lorwyn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (147,'Manticore');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (148,'Masticore');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (149,'Meditation');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (150,'Mercadia');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (151,'Mercenary');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (152,'Merfolk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (153,'Metathran');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (154,'Mine');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (155,'Minion');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (156,'Minotaur');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (157,'Mirrodin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (158,'Moag');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (159,'Monger');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (160,'Mongoose');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (161,'Mongseng');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (162,'Monk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (163,'Moonfolk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (164,'Mountain');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (165,'Muraganda');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (166,'Mutant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (167,'Myr');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (168,'Mystic');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (169,'Nautilus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (170,'Nephilim');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (171,'New');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (172,'Nightmare');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (173,'Nightstalker');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (174,'Ninja');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (175,'Nissa');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (176,'Noggle');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (177,'Nomad');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (178,'Octopus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (179,'Ogre');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (180,'Ooze');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (181,'Orc');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (182,'Orgg');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (183,'Ouphe');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (184,'Ox');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (185,'Oyster');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (186,'Pegasus');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (187,'Pest');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (188,'Phelddagrif');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (189,'Phoenix');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (190,'Phyrexia');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (191,'Pirate');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (192,'Plains');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (193,'Plant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (194,'Power-Plant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (195,'Praetor');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (196,'Rabbit');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (197,'Rabiah');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (198,'Rat');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (199,'Rath');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (200,'Ravnica');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (201,'Realm');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (202,'Rebel');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (203,'Regatha');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (204,'Rhino');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (205,'Rigger');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (206,'Rogue');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (207,'Salamander');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (208,'Samurai');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (209,'Sarkhan');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (210,'Satyr');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (211,'Scarecrow');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (212,'Scorpion');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (213,'Scout');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (214,'Segovia');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (215,'Serpent');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (216,'Serra\'s');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (217,'Shade');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (218,'Shadowmoor');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (219,'Shaman');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (220,'Shandalar');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (221,'Shapeshifter');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (222,'Sheep');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (223,'Shrine');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (224,'Siren');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (225,'Skeleton');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (226,'Slith');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (227,'Sliver');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (228,'Slug');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (229,'Snake');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (230,'Soldier');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (231,'Soltari');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (232,'Sorin');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (233,'Spawn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (234,'Specter');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (235,'Spellshaper');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (236,'Sphinx');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (237,'Spider');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (238,'Spike');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (239,'Spirit');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (240,'Sponge');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (241,'Squid');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (242,'Squirrel');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (243,'Starfish');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (244,'Surrakar');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (245,'Swamp');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (246,'Tamiyo');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (247,'Tezzeret');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (248,'Thalakos');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (249,'Thopter');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (250,'Thrull');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (251,'Tibalt');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (252,'Tower');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (253,'Trap');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (254,'Treefolk');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (255,'Troll');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (256,'Turtle');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (257,'Ulgrotha');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (258,'Unicorn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (259,'Urza\'s');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (260,'Valla');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (261,'Vampire');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (262,'Vedalken');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (263,'Venser');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (264,'Viashino');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (265,'Volver');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (266,'Vraska');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (267,'Vryn');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (268,'Wall');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (269,'Warrior');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (270,'Weird');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (271,'Werewolf');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (272,'Whale');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (273,'Wildfire');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (274,'Wizard');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (275,'Wolf');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (276,'Wolverine');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (277,'Wombat');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (278,'Worm');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (279,'Wraith');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (280,'Wurm');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (281,'Xerex');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (282,'Yeti');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (283,'Zendikar');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (284,'Zombie');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (285,'Zubera');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (286,'Beck');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (287,'Guy');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (288,'Asia');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (289,'Nymph');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (290,'God');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (291,'Ashiok');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (292,'Xenagos');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (293,'Sable');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (294,'Rider');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (295,'Urza\'s');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (296,'Power-Plant');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (297,'Mine');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (298,'Tower');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (299,'Lamia');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (300,'Kiora');
INSERT INTO `subtypes` (`id`, `subtype`) VALUES (301,'Ral');
/*!40000 ALTER TABLE `subtypes` ENABLE KEYS */;
UNLOCK TABLES;
