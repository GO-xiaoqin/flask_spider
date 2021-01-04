CREATE TABLE houses_city(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `houses` VARCHAR(50) DEFAULT NULL,
    `area_code` VARCHAR(50) DEFAULT NULL,
    `city_code` VARCHAR(50) DEFAULT NULL,
    unique index(`houses`, `area_code`, `city_code`),
    PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;