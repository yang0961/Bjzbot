# coding: utf-8
# @Author: 小杨大帅哥
import sys
import logging
handler = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(handler)

from loguru import logger


