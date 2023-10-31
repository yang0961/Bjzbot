# coding: utf-8
# @Author: 小杨大帅哥
import asyncio
import json
import os.path
import sys
from pathlib import Path
from sender import Account
import yaml
from config import con_json
from log import logger
from service.receive import rgt, Receiver
from typing import Callable
from message import Message
from abc import abstractmethod

rgt: Receiver


class Register(object):
    def __init__(self):
        logger.debug("正在初始化中, 请稍后")
        self.__setting()
        self.__isLogin()

    @abstractmethod
    def message_register(self,
                         isGroup: bool = False,
                         isDivision: bool = False):
        """
        外部可访问接口
        [所有消息] 处理函数注册器, 用来接受异步函数
        参数:
        :param isGroup 对消息进行限制, 当为True时, 只接受群消息, 当为False时, 只接受私聊消息,
                       注意! 仅当isDivision为 True时, isGroup参数生效
        :param isDivision 是否对消息分组
        """
        return rgt.message_register(isGroup=isGroup,
                                    isDivision=isDivision)

    @abstractmethod
    def revoke_message_register(self,
                                isGroup: bool = False,
                                isDivision: bool = False,
                                allow_other_receive: bool = True):
        """
        外部可访问接口
        [撤回消息] 处理函数注册器, 用来接受异步函数
        参数:
        :param isGroup 对消息进行限制, 当为True时, 只接受群消息, 当为False时, 只接受私聊消息,
                       注意! 仅当isDivision为 True时, isGroup参数生效
        :param isDivision 是否对消息分组
        :param allow_other_receive 是否允许符合本函数要求的消息(撤回消息)被其他消息函数(指函数类名不同且
                                    必须同为同一个 kind的消息函数(即同为异步或者同步))接受
        """
        return rgt.revoke_message_register(isGroup=isGroup,
                                           isDivision=isDivision,
                                           allow_other_receive=allow_other_receive)

    @abstractmethod
    def group_changed_register(self,
                               allow_other_receive: bool = True):
        """
        外部可访问接口
        [群成员变动消息]处理函数注册器, 用来接受异步函数
        参数:
        :param allow_other_receive 是否允许符合本函数要求的消息(群成员消息)被其他消息函数(指函数类名不同且
                                    必须同为同一个 kind的消息函数(即同为异步或者同步))接受
        """
        return rgt.group_changed_register(allow_other_receive=allow_other_receive)

    @abstractmethod
    def custom_message_register(self,
                                register_name: str,
                                msg_judge_func: Callable[[Message], bool],
                                allow_other_receive: bool,
                                isGroup: bool = False,
                                isDivision: bool = False):
        """
        外部可访问接口
        [自定义消息]处理函数注册器, 用来接受异步函数
        参数:
        :param isGroup 对消息进行限制, 当为True时, 只接受群消息, 当为False时, 只接受私聊消息,
                       注意! 仅当isDivision为 True时, isGroup参数生效
        :param isDivision 是否对消息分组
        :param register_name 注册函数类名, 注意不可为空, 注意函数类名决定最后消息分发结果, 因此每个新函数的类名应是不同的
        :param msg_judge_func 判断消息是否为符合自定义消息的函数 (函数直接受一个参数 WcfMsg作为参数, 返回值为 bool)
                                    在函数内编写需要符合自定义要求的函数, 但函数返回值必须为 bool类型, 符合要求返回 True,
                                    不符合要求返回 False
        :param allow_other_receive 是否允许符合本函数要求的消息(自定义符合消息)被其他消息函数(指函数类名不同且
                                    必须同为同一个 kind的消息函数(即同为异步或者同步))接受
        """
        return rgt.custom_message_register(register_name=register_name,
                                           msg_judge_func=msg_judge_func,
                                           allow_other_receive=allow_other_receive,
                                           isGroup=isGroup,
                                           isDivision=isDivision)

    @abstractmethod
    def run(self, print_msg: bool = True, thread_proces_msg: bool = False):
        """
        启动程序, 开始接受消息
        :param 打印消息
        """
        return rgt.run(print_msg=print_msg,
                       thread_proces_msg=thread_proces_msg)



    @property
    def __config(self):
        config_json = """
# BjzBot配置
BjzBot:
  # OPQ登录中的 QQ, 必填项, 填错程序将会报错
  QQ: 
  # OPQ中设置的 host, 可选项, 若不填写, 默认为 127.0.0.1
  host: 127.0.0.1
  # OPQ中设置的 port, 可选项, 若不填写, 默认为 8086
  port: 8086
        """
        return config_json

    def __setting(self):
        if not (c_yaml := Path("config.yml")).exists():
            with c_yaml.open(mode="w", encoding="utf-8") as f:
                f.write(self.__config)
            logger.debug("请先填写配置文件 config.yml, 程序退出")
            sys.exit(0)
        yaml_data = yaml.load(c_yaml.open(mode="r", encoding="utf-8").read(),
                              Loader=yaml.FullLoader)["BjzBot"]
        if yaml_data["QQ"] is None:
            logger.error("请在config.yaml填写 QQ")
            raise ValueError("请在config.yaml填写 QQ")
        config = Path(str(Path(__file__).parent.parent) + r"\config\settings.json")
        with config.open(mode='w', encoding="UTF-8") as file:
            file.write(json.dumps(
                {
                    "QQ": yaml_data["QQ"],
                    "host": yaml_data["host"] if yaml_data["host"] else "127.0.0.1",
                    "port": yaml_data["port"] if yaml_data["port"] else 8086,
                },
                ensure_ascii=False, indent=4
            ))
            logger.debug("初始化完成")
            logger.debug(f"创建 websocket实例 ws://{yaml_data['host']}:{yaml_data['port']}/wx")
            logger.debug("连接 OPQ中, 请等待")

    def __isLogin(self):
        async def _login():
            logger.debug("正在校验是否已登录...")
            accu = Account()
            res = await accu._login()
            while True:
                if res["ResponseData"]:
                    if [True for ele in res["ResponseData"]["QQUsers"] if ele["Uin"] == con_json.QQ][0]:
                        break
                logger.error('网络断开或不可用, 请检查网络')
                logger.error(f'{res["CgiBaseResponse"]["ErrMsg"]}')
                logger.debug("正在重连中...")
                await asyncio.sleep(2)
            logger.debug("账号在线")
        asyncio.get_event_loop().run_until_complete(_login())


