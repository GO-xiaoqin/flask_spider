CREATE TABLE ershou_area_ke(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `area` VARCHAR(50) DEFAULT NULL,
    `area_code` VARCHAR(50) DEFAULT NULL,
    `city_id` INT(11) UNSIGNED NOT NULL,
    unique index(`area` ,`area_code`),
    PRIMARY KEY (`id`),
    FOREIGN KEY(`city_id`) REFERENCES provice_city_ke(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;