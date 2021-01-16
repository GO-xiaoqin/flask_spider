CREATE TABLE houses_city_ke(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `houses` VARCHAR(50) DEFAULT NULL,
    `area_code` VARCHAR(50) DEFAULT NULL,
    `city_code` VARCHAR(50) DEFAULT NULL,
    unique index(`city_code`, `area_code`, `houses`),
    PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8 comment='存储抓取下来的每个类型的名字以及所在城市区域';