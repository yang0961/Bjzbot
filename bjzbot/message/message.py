# coding: utf-8
# @Author: 小杨大帅哥
import traceback
from abc import abstractmethod

class Message(dict):
    """
    消息基类
    所见消息内容都可以通过 . 的方法获得, 例: message.user_id
    内置消息方法 [
        {{isGroup}},
        {{isBot}},
        {{botId}},
        {{text}},
        {{groupId}},
        {{senderId}}
        {{havingImage}}
        {{getImage}},
        {{getVideo}},
        {{getVoice}},
        {{isAt}}
    ]
    """

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        if not self.__contains__(key):
            traceback.print_exc()
        value = self[key]
        if isinstance(value, (dict, list)):
            if isinstance(value, list):
                return [Message(item) if isinstance(item, dict) else item for item in value]
            return Message(value)
        return value

    @property
    @abstractmethod
    def isGroup(self) -> bool or None:
        """
        是否是群消息
        :return: 消息属于正常消息, return bool
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def isBot(self) -> bool or None:
        """
        是否是 Bot消息
        :return: 消息属于正常消息, return bool
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def botId(self) -> int or None:
        """
        获取 Bot的账号
        :return: 消息属于正常消息, return int
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def text(self) -> str or None:
        """
        获取消息内容
        :return: 消息属于正常消息, return message.content内容
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def groupId(self) -> int or None:
        """
        获取消息发送的群号
        :return: 消息属于正常消息, return bool
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def senderId(self) -> int or None:
        """
        获得消息的发送者 Id
        :return: int or None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def havingImage(self) -> bool or None:
        """
        判断消息内是否含有照片
        :return 消息属于正常消息, return bool
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def getImage(self) -> str or None:
        """
        获得消息中的图片 url地址
        :return url else: None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def getVideo(self) -> str or None:
        """
        获得消息中的视频 url地址
        :return url else: None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def getVoice(self) -> str or None:
        """
        获得消息中的语音 url地址
        :return url else: None
        """
        raise NotImplementedError()

    @abstractmethod
    def is_at(self, include_at_all=True) -> bool or None:
        """
        是否被 at
        :param include_at_all: 是否包含 at全体成员
        :return 消息属于正常消息, return bool
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def getReplyParams(self) -> dict or None:
        """
        获取回复消息时所需要的参数
        :return: 消息属于正常消息, return dict
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def getGroupInfo(self) -> dict or None:
        """
        获取群消息的群概况
        :return: return dict
                 else: return None
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def isUsefulMsg(self) -> bool:
        """
        消息是否同时包含 MsgHead 和 MsgBody 两部分
        :return: return bool
        """
        raise NotImplementedError()


