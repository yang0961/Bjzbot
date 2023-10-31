# coding: utf-8
# @Author: 小杨大帅哥

import nest_asyncio
import asyncio
import functools
import json
from log import logger
import random
import traceback
from ..config import con_json
from websockets.exceptions import ConnectionClosedError as ws_ConnectionClosedError
from typing import Callable, Any
from ..message import Message
from ..sender import Account
import websockets
nest_asyncio.apply(asyncio.get_event_loop())


def load_function(cls):
    cls._receive_msg = _receive_msg
    cls._register = _register
    cls._processing_message_func = _processing_message_func
    cls.message_register = message_register
    cls.revoke_message_register = revoke_message_register
    cls.group_changed_register = group_changed_register
    cls.custom_message_register = custom_message_register
    cls.run = run
    return cls


async def _receive_msg(self):
    """有消息的时候，通知分发器分发消息"""
    try:
        async with websockets.connect(f"ws://{self._host_port}/ws") as websocket:
            if self._first_start:
                await asyncio.sleep(2.8)
                logger.debug(f"OPQ连接成功, 开始接收消息")
                logger.debug(f"登录账号为 Account <{con_json.QQ}>")
                await asyncio.sleep(0.2)
            while True:
                str_message = await websocket.recv()
                self._first_start = False
                if str_message:
                    if self._show_msg:
                        logger.info(f"收到消息: {str_message}")
                    self._message = Message(json.loads(str_message))
                    if self._thread_flag:
                        self._run_in_thread()
                        continue
                    await self._run_func()
    except ws_ConnectionClosedError:
        # 断线重连
        logger.error(f"OPQ或被关闭, 连接已断开, 程序等待重连中...")
        self._retry = True
        self._first_start = True
        await asyncio.sleep(random.randint(5, 8))
        await self._receive_msg()
    except ConnectionRefusedError:
        if self._retry:
            return await self._receive_msg()
        logger.error(f"host或者port配置错误, 或OPQ未开启, 造成远程计算机拒绝网络连接")
        raise ConnectionRefusedError(f"host或者port配置错误, 或 OPQ未开启, 造成远程计算机拒绝网络连接")
    except:
        traceback.print_exc()


def _register(self,
              register_name: str,
              allow_other_receive: bool,
              judge_msg: Callable[[Any], Any]):
    def __register(func: Callable[[Any], Any]):
        self._add_callback(func,
                           register_name=register_name,
                           allow_other_rec=allow_other_receive,
                           judge_msg=judge_msg)
        # 此处必须返回被装饰函数原函数, 否则丢失被装饰函数信息
        return func

    return __register


def _processing_message_func(self,
                             isGroup: bool,
                             isDivision: bool,
                             register_name: str,
                             allow_other_receive: bool,
                             judge_msg: Callable[[Any], bool]):
    def _async_func(func):
        @functools.wraps(func)
        @self._register(register_name, allow_other_receive, judge_msg)
        async def __async_func(bot: Account, message: Message):
            try:
                # 判断被装饰函数是否为协程函数, 本函数要求是协程函数
                if not asyncio.iscoroutinefunction(func):
                    raise ValueError(f'这里应使用协程函数, 而被装饰函数-> ({func.__name__}) <-是非协程函数')
                if not isDivision:
                    return await func(bot, message)
                if message.isGroup and isGroup:
                    return await func(bot, message)
                if not message.isGroup and not isGroup:
                    return await func(bot, message)
            except:
                traceback.print_exc()

        return __async_func

    return _async_func


def revoke_message_register(self,
                            isGroup: bool = False,
                            isDivision: bool = False,
                            allow_other_receive: bool = True):
    def judge_msg(msg):
        if msg.CurrentPacket.EventData.EventName == "ON_EVENT_GROUP_MSG_REVOKE":
            return True
        return False

    return self._processing_message_func(isGroup,
                                         isDivision,
                                         register_name='revokeMessage',
                                         allow_other_receive=allow_other_receive,
                                         judge_msg=judge_msg)


def group_changed_register(self,
                           allow_other_receive: bool = True):
    def judge_msg(msg):
        if not msg.isGroup:
            return False
        if msg.CurrentPacket.EventData.EventName == "ON_EVENT_GROUP_EXIT" or\
            msg.CurrentPacket.EventData.EventName == "ON_EVENT_GROUP_JOIN":
            return True
        return False

    return self._processing_message_func(isGroup=True,
                                         isDivision=True,
                                         register_name='groupChanged',
                                         allow_other_receive=allow_other_receive,
                                         judge_msg=judge_msg)


def custom_message_register(self,
                            register_name: str,
                            msg_judge_func: Callable[[Message], bool],
                            allow_other_receive: bool,
                            isGroup: bool = False,
                            isDivision: bool = False):
    return self._processing_message_func(isGroup,
                                         isDivision,
                                         register_name=register_name,
                                         allow_other_receive=allow_other_receive,
                                         judge_msg=msg_judge_func)


def message_register(self,
                     isGroup: bool = False,
                     isDivision: bool = False):
    return self._processing_message_func(isGroup,
                                         isDivision,
                                         register_name='common',
                                         allow_other_receive=True,
                                         judge_msg=lambda x: True)


def run(self, print_msg: bool = True, thread_proces_msg: bool = False):
    self._thread_flag = thread_proces_msg
    self._show_msg = print_msg
    try:
        asyncio.get_event_loop().run_until_complete(self._receive_msg())
    except KeyboardInterrupt:
        logger.debug('程序已退出, 停止接收消息')
