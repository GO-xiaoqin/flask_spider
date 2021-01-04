CREATE TABLE houses_info(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `houses_title` VARCHAR(50) DEFAULT NULL comment '楼盘名字',
    `houses_type` INT(8) DEFAULT NULL comment '楼盘类型: 1住宅，2别墅，3商业，4写字楼，5底商',
    `houses_status` INT(8) DEFAULT NULL comment '楼盘状态: 1在售，2下期待开，3未开盘',
    `houses_location` VARCHAR(50) DEFAULT NULL,
    `houses_room`  VARCHAR(50) DEFAULT NULL comment '楼盘户型',
    `houses_tag` VARCHAR(50) DEFAULT NULL comment '楼盘标签',
    `houses_price`  VARCHAR(50) DEFAULT NULL,
    `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
    `updatetime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `houses_id` INT(11) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    unique index(`houses_id`, `houses_price`),
    FOREIGN KEY(`houses_id`) REFERENCES houses_city(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;