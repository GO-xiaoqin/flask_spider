CREATE TABLE `provice_city` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `city` VARCHAR(10) DEFAULT NULL,
  `city_code` VARCHAR(50) DEFAULT NULL,
  `provice` VARCHAR(50) DEFAULT NULL,
  unique index(`city` ,`city_code`),
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;