# -*- coding: utf-8 -*-
from abc import abstractmethod
import logging
from typing import Callable, Any
from sender import Account
from message import Message
import asyncio


class Event(object):
    _cbFunc = {}
    _loop_flag = False
    _thread_flag = False
    _inCache = False
    _message_callback_func_list = []
    _loop = asyncio.get_event_loop()
    _filter_cache = {}
    _kind_dict = {}

    def __init__(self):
        super(Event, self).__init__()
        self._message = None
        self._thread_flag = False
        self._show_msg = True
        self._logger: logging = logging.getLogger()

    @abstractmethod
    def _add_callback(self,
                      func: Callable[[Any], Any],
                      register_name: str,
                      allow_other_rec: bool,
                      judge_msg: Callable[[Message], bool]):
        """
        消息处理函数加载器
        :param func: 装饰器装饰的函数
        :param register_name: 装饰器所处类别下的函数类名(主要区分不同装饰器的作用, 以及为其中的 allow_other_rec参数做准备)
        :param allow_other_rec: 是否允许消息分发到其他不同类名装饰器(该参数对不同函数类(register_name)装饰器有效)
        :param judge_msg: 判断是否为该装饰器所处理的消息的函数
        """
        raise NotImplementedError

    @abstractmethod
    def _run_func(self):
        """
        消息分发器, 将消息发送给可接受消息的消息处理函数
        """
        raise NotImplementedError

    def _run_in_thread(self):
        pass

