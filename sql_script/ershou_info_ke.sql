CREATE TABLE ershou_info_ke(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `ershou_name` VARCHAR(100) DEFAULT NULL comment '楼房名字',
    `positioninfo` VARCHAR(100) DEFAULT NULL comment '位置信息',
    `houseinfo` VARCHAR(150) DEFAULT NULL,
    `followinfo` VARCHAR(50) DEFAULT NULL comment '信息度信息',
    `tag`  VARCHAR(50) DEFAULT NULL comment '标签',
    `priceinfo` VARCHAR(50) DEFAULT NULL comment '参考价格',
    `createtime` datetime DEFAULT CURRENT_TIMESTAMP,
    `updatetime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `xiaoqu_id` INT(11) UNSIGNED NOT NULL,
    `houses_id` INT(11) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    unique index(`houses_id`, `tag`, `priceinfo`),
    FOREIGN KEY(`xiaoqu_id`) REFERENCES xiaoqu_detail_ke(id),
    FOREIGN KEY(`houses_id`) REFERENCES houses_city_ke(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;