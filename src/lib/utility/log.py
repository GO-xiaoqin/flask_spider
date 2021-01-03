#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。

import logging
import  sys
from src.lib.utility.path import LOG_PATH

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
# 创建一个流处理器handler并设置其日志级别为DEBUG
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
# 创建一个格式器formatter并将其添加到处理器handler
formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s")
handler.setFormatter(formatter)
# 为日志器logger添加上面创建的处理器handler
logger.addHandler(handler)


# handler = logging.FileHandler(LOG_PATH + "/log.txt")
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

if __name__ == '__main__':
    pass
