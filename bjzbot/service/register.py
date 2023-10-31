# coding: utf-8
# @Author: 小杨大帅哥
import asyncio
import sys
from ..sender import Account
from ..config import con_json
from ..log import logger
from ..service.receive import rgt, Receiver
from typing import Callable
from ..message import Message
from abc import abstractmethod

rgt: Receiver


class Register(object):
    def __init__(self):
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

    def __isLogin(self):
        async def _login():
            logger.debug("正在校验是否已登录...")
            accu = Account()
            res = await accu._login()
            if (_data := res["CgiBaseResponse"])["Ret"] == 0:
                logger.debug("账号在线")
                return True
            return False
        if not asyncio.get_event_loop().run_until_complete(_login()):
            logger.debug("账号未登录")
            url = f"http://{con_json.host}:{con_json.port}/v1/login/getqrcode?qq={con_json.QQ}&devicename=QQ_Windows"
            logger.debug(f"请先点击该网址登录账号, 在 OPQ确认登录后再次启动程序 \nLogin url: {url}")
            sys.exit(0)

