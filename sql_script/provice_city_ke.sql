CREATE TABLE `provice_city_ke` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `city` VARCHAR(10) DEFAULT NULL comment '贝壳网的城市名称',
  `city_code` VARCHAR(50) DEFAULT NULL,
  `city_href` VARCHAR(200) DEFAULT NULL,
  `city_status` INT(11) DEFAULT NULL comment '贝壳网城市是否有二手楼房信息 1 有 0 没有只有新房楼盘信息',
  `provice` VARCHAR(50) DEFAULT NULL,
  unique index(`city` ,`city_code`),
  PRIMARY KEY (`id`)
) ENGINE=INNODB DEFAULT CHARSET=utf8;