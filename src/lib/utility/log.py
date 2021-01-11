#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。

import logging

LOG_FORMAT = "%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

logger = logging


if __name__ == '__main__':
    pass
