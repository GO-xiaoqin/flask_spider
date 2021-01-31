CREATE TABLE xiaoqu_info_ke(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `xiaoqu_name` VARCHAR(50) DEFAULT NULL comment '楼盘名字',
    `houseinfo` VARCHAR(150) DEFAULT NULL,
    `positioninfo` VARCHAR(100) DEFAULT NULL comment '位置信息',
    `taglist` VARCHAR(50) DEFAULT NULL,
    `price`  VARCHAR(50) DEFAULT NULL comment '参考价格',
    `on_sale` VARCHAR(50) DEFAULT NULL comment '在售楼房数量',
    `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
    `updatetime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `xiaoqu_id` INT(11) UNSIGNED NOT NULL,
    `houses_id` INT(11) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    unique index(`houses_id`, `price`, `on_sale`),
    FOREIGN KEY(`xiaoqu_id`) REFERENCES xiaoqu_detail_ke(id),
    FOREIGN KEY(`houses_id`) REFERENCES houses_city_ke(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;