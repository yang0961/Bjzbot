# coding: utf-8
# @Author: 小杨大帅哥
from json import load
from pathlib import Path



class Config(object):
    __c_j = load(Path(str(Path(__file__).parent) + r"\settings.json").open(mode="r", encoding="utf-8"))
    QQ = __c_j["QQ"]
    host = __c_j["host"]
    port = __c_j["port"]



con_json = Config()

