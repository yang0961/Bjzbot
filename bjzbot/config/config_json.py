# coding: utf-8
# @Author: 小杨大帅哥
import sys
import yaml
from log import logger
from pathlib import Path

logger.debug("正在初始化中, 请稍后")
__config = """
# BjzBot配置
BjzBot:
  # OPQ登录中的 QQ, 必填项, 填错程序将会报错
  QQ: 
  # OPQ中设置的 host, 可选项, 若不填写, 默认为 127.0.0.1
  host: 127.0.0.1
  # OPQ中设置的 port, 可选项, 若不填写, 默认为 8086
  port: 8086
"""

if not (c_yaml := Path("config.yml")).exists():
    with c_yaml.open(mode="w", encoding="utf-8") as f:
        f.write(__config)
    logger.debug("config.yml配置文件不存在, 已自动生成")
    logger.debug("请先填写配置文件 config.yml, 程序退出")
    sys.exit(0)
yaml_data = yaml.load(c_yaml.open(mode="r", encoding="utf-8").read(),
                      Loader=yaml.FullLoader)["BjzBot"]
if yaml_data["QQ"] is None:
    logger.error("请在config.yaml填写 QQ")
    raise ValueError("请在config.yaml填写 QQ")

logger.debug("初始化完成")
logger.debug(f"创建 websocket实例 ws://{yaml_data['host']}:{yaml_data['port']}/ws")
logger.debug("连接 OPQ中, 请等待")


class Config(object):
    QQ = yaml_data["QQ"]
    host = yaml_data["host"] if yaml_data["host"] else "127.0.0.1"
    port = yaml_data["port"] if yaml_data["port"] else 8086


con_json = Config()

