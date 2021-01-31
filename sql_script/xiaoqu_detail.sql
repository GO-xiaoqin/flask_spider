CREATE TABLE xiaoqu_detail_ke(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `xiaoqu_title` VARCHAR(100) DEFAULT NULL comment '楼盘名字',
    `building_type` VARCHAR(100) DEFAULT NULL,
    `property_expenses` VARCHAR(100) DEFAULT NULL,
    `property_company` VARCHAR(100) DEFAULT NULL,
    `developer` VARCHAR(150) DEFAULT NULL,
    `total_number_of_buildings` VARCHAR(100) DEFAULT NULL,
    `total_number_of_houses` VARCHAR(100) DEFAULT NULL,
    `nearby_stores` VARCHAR(200) DEFAULT NULL,
    `lat` FLOAT DEFAULT NULL,
    `lng` FLOAT DEFAULT NULL,
    PRIMARY KEY (`id`),
    unique index(`xiaoqu_title`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;