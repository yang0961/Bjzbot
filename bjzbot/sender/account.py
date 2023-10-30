# coding: utf-8
# @Author: 小杨大帅哥
import asyncio
import json
from typing import List, Dict, Any, AsyncIterator

from exception import SendError
import traceback
from log import logger
from sender.const import *
from pathlib import Path
import aiohttp


def _catch_error(_return=None, fun=None):
    def _catch(func):
        async def __catch(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except:
                if fun is not None:
                    func()
                logger.error(f'{_return}\n{str(traceback.format_exc())}')

        return __catch

    return _catch


class Account(object):
    def __init__(self):
        self.__tasks = []
        self.__url = ""
        self.__last = ""
        self.__send_url = 'http://127.0.0.1:8086/v1/LuaApiCaller?qq=1928658864&funcname=MagicCgiCmd&timeout=10'
        self.__upload_url = 'http://127.0.0.1:8086/v1/upload?qq=1928658864'
        self.__send_group = False
        self.__headers = {
            'user_agent': 'Mozilla/5.0 (Android 6.0.1; Mobile; rv:38.0) Gecko/38.0 Firefox/38.0',
            'Content-Type': 'application/json'
        }
        self.__send_body: Dict[str, Any] = {
            "CgiCmd": "MessageSvc.PbSendMsg",
            "CgiRequest": {
                "ToUin": 0,
                "ToType": 0,
                "Content": "",
            }
        }

    def send_content(self, text: str):
        logger.info("发送文字消息")
        if not text:
            raise ValueError("发送文字消息不能为空")
        self.__send_body['CgiRequest']['Content'] = str(text)
        return self

    def send_image(self,
                   file_path: str or List[str] = None,
                   file_url: str or List[str] = None,
                   file_base64: str or List[str] = None):
        """
         照片可以发送多张, 即可同时多次.send_image
        :param file_path: 图片路径
        :param file_url: 图片链接
        :param file_base64: 图片 base64
        :return: 消息发送后返回结果
        """
        func_vars = {'file_path': file_path, 'file_url': file_url, 'file_base64': file_base64}
        if not [ele for ele in func_vars.values() if (ele is not None) and not ele]:
            raise ValueError('必须有一个参数不为空')
        # if isinstance((file_path, file_url, file_base64), str):
        #     user_uin = [user_uin]
        # elif isinstance(user_uin, list):
        #     if not user_uin:
        #         raise ValueError('请传入需要 at的用户 QQUin')
        #     for ele in user_uin:
        #         if not isinstance(ele, int):
        #             raise ValueError('user_uin必须是整型')
        # else:
        #     raise ValueError('user_uin必须是整型')
        # if not isinstance(str, (file_path, file_url, file_base64)):
        #     raise ValueError("file_path, file_url, file_base64 必须是字符串")
        return self.__send(name="照片", error_tips="部分照片发送失败", send_body="FileId", _type="image",
                           send_type="Images", file_path=file_path, file_url=file_url, file_base64=file_base64)

    def send_voice(self, file_path=None, file_url=None):
        """
        语音不可以发送很多次, 即每次只能出现一次, send_voice, 多次出现只发送最后一条语音
        语音不可以和其他的发送连在一起, 连在一起后
        只会发送语音, 其他发送操作失效或者导致消息全部发送失败
        :param file_path: 音频路径
        :param file_url: 音频链接
        两个参数 file_path, file_url同时存在时, 按照参数位置从左到右取第一个
        :return: 消息发送后返回结果
        """
        for _item in (file_path, file_url):
            if not isinstance(_item, str):
                raise ValueError("file_path, file_url, file_base64 必须是字符串")
        return self.__send("语音", "语音发送失败", "FileToken", "voice", "Voice",
                           file_path=file_path, file_url=file_url, file_base64=None)

    def send_msg_reply(self, msg_seq: int, msg_time: int, msg_uid: int, replay_sender_id: int):
        """
        注意需要回复的信息必须是 replay_sender_id发送, 并且分清私聊和组, 不然可能会出现意外之错
        :param msg_seq: 消息序号
        :param msg_time: 消息时间
        :param msg_uid: 消息 uid
        :param replay_sender_id 消息的发送者 QQUin
        :return:
        """
        for _item in (msg_seq, msg_time, msg_uid, replay_sender_id):
            if not isinstance(_item, int):
                raise ValueError("所有参数必须都是整型")

        async def _reply():
            self.__send_body["CgiRequest"]['ReplyTo'] = {
                "MsgSeq": msg_seq,
                "MsgTime": msg_time,
                "MsgUid": msg_uid}
            if self.__send_group:
                self.at(replay_sender_id)

        self.__tasks.append(_reply)
        return self

    def send_group_file(self, file_name: str, file_path: str, notify: bool = True):
        for ele in (file_name, file_path):
            if not isinstance(ele, str):
                raise ValueError("所有参数必须都是字符串")

        async def _group_file():
            if not self.__send_group:
                raise SendError("send_group_file只能用于群聊")
            self.__send_body['CgiCmd'] = "PicUp.DataUp"
            for _item in self.__send_body['CgiRequest']:
                self.__send_body['CgiRequest'] = {"CommandId": GROUP_FILE_COMMAND_ID, "FileName": file_name,
                                                  "FilePath": file_path, "Notify": notify,
                                                  "ToUin": self.__send_body['CgiRequest']["ToUin"]}

        self.__tasks.append(_group_file)
        return self

    def send_group_json(self, content: dict):
        """
        不可与其他发送操作链式调用
        框架正在开发中, 并不完善, 可能出现发送不成功的现象
        发送群组卡片 json消息
        :param content: JSON内容 需自行转义
        """
        self.__send_body['CgiRequest']['Content'] = json.dumps(content)
        self.__send_body['CgiRequest']["SubMsgType"] = SUB_MSG_TYPE

        async def _json():
            if not self.__send_group:
                raise SendError("send_json只可以发送给群组")

        self.__tasks.append(_json)
        return self

    def at(self, user_uin: int or List[int]):
        """
        发送 at 消息
        :param user_uin: at对象 QQUin, 0代表全体成员,
                在 at全体成员时, 仅当 bot账号是群管理员或群主, 且有剩余 at全体成员次数时, 才会成功发送, 否则抛出错误
        """
        logger.info("发送 at消息")
        if isinstance(user_uin, int):
            user_uin = [user_uin]
        elif isinstance(user_uin, list):
            if not user_uin:
                raise ValueError('请传入需要 at的用户 QQUin')
            for ele in user_uin:
                if not isinstance(ele, int):
                    raise ValueError('user_uin必须是整型')
        else:
            raise ValueError('user_uin必须是整型')

        async def __at():
            if not self.__send_group:
                raise SendError("非群聊不可使用 at方法")
            if self.__send_body['CgiRequest'].get('AtUinLists', None) is None:
                self.__send_body['CgiRequest']['AtUinLists'] = []
            self.__send_body['CgiRequest']['AtUinLists'].extend([{"Nick": str(ele), 'Uin': ele} for ele in user_uin])

        self.__tasks.append(__at)
        return self

    async def to_friend(self, friend_id: int):
        return await self.__to(friend_id, 1)

    async def to_private(self, private_id: int, group_id: int):
        self.__send_body['CgiRequest']['GroupCode'] = group_id

        async def __private():
            if self.__send_body['CgiRequest']['ReplyTo']:
                raise ValueError("私聊不允许回复消息")

        self.__tasks.append(__private)
        return await self.__to(private_id, 3)

    async def to_group(self, group_id: int):
        self.__send_group = True
        return await self.__to(group_id, 2)

    async def get_group_members(self, group_id) -> AsyncIterator:
        """
        获取群成员列表, 一次最多返回 500个
        :param group_id: 群组 id
        :return: AsyncIterator [MemberLists]
        """
        LastBuffer = ""
        while True:
            _send_b = {
                "CgiCmd": "GetGroupMemberLists",
                "CgiRequest": {
                    "Uin": group_id,
                    "LastBuffer": LastBuffer
                }
            }
            result: dict = await asyncio.wait_for(asyncio.create_task(
                self.__request_http("POST", url=self.__send_url, headers=self.__headers, json=_send_b)
            ), 10)
            if result["ResponseData"]["MemberLists"]:
                LastBuffer = result["ResponseData"]["LastBuffer"]
            yield result["ResponseData"]["MemberLists"]
            if not LastBuffer:
                break

    async def get_friend_list(self) -> AsyncIterator:
        """
        暂定有问题
        :return:
        """
        while True:
            _send_b = {
                "CgiCmd": "GetFriendLists",
                "CgiRequest": {
                    "LastUin": 1928658864
                }
            }
            result: dict = await asyncio.wait_for(asyncio.create_task(
                self.__request_http("POST", url=self.__send_url, headers=self.__headers, json=_send_b)
            ), 10)
            yield result["ResponseData"]
            break

    async def get_self_info(self) -> dict:
        _send_by = {
            "CgiCmd": "ClusterInfo",
            "CgiRequest": {}
        }
        result: dict = await asyncio.wait_for(asyncio.create_task(
            self.__request_http("POST", url=self.__send_url, headers=self.__headers, json=_send_by)
        ), 10)
        return result['ResponseData']

    async def __request_http(self, method: str, *args, p_error=True, **kwargs):
        try:
            print('kwars', kwargs)
            async with aiohttp.ClientSession(loop=asyncio.get_running_loop(),
                                             timeout=aiohttp.ClientTimeout(total=10)) as session:
                request = session.post
                if method.lower() == 'get':
                    request = session.get
                async with request(*args, **kwargs) as response:
                    result = await response.json()
                    print('result', result)
                    if not p_error:
                        return result
                    if "v1/upload" in kwargs['url']:
                        return result
                    if (error_tip := result['CgiBaseResponse'])['Ret'] != 0:
                        logger.error(
                            f"消息发送失败 -> 失败原因 {error_tip['ErrMsg'] if error_tip['ErrMsg'] else None} - 发送对象: {kwargs['json']['CgiRequest']['ToUin']}")
                        raise SendError(
                            f"发送失败-> 失败原因 {error_tip['ErrMsg'] if error_tip['ErrMsg'] else None} - 发送对象: {kwargs['json']['CgiRequest']['ToUin']}")
                    return result
        except json.decoder.JSONDecodeError:
            logger.error(f"消息发送失败, 请确认 OPQ是否完整")
        except:
            logger.error(f"发送失败, 返回结果为-> \n{traceback.format_exc()}")

    async def __to(self, sender_id: int, to_type: int):
        self.__send_body['CgiRequest']['ToUin'] = sender_id
        print('sender_id', sender_id)
        if self.__send_body['CgiRequest'].get("ToType", None) is not None:
            self.__send_body['CgiRequest']['ToType'] = to_type
        print('tasks', self.__tasks)
        if len(self.__tasks) != 0:
            # 原本应该直接将异步任务一起运行, 但是接口不允许并发请求, 因此改为一个一个请求接口
            for task in self.__tasks:
                await asyncio.wait_for(asyncio.create_task(task()), 10)
        print('self.__send_body', self.__send_body)
        if self.__send_body["CgiCmd"] == "MessageSvc.PbSendMsg":
            self.__url = self.__send_url
            if not self.__send_body['CgiRequest']['Content'] and \
                    (self.__send_body['CgiRequest'].get('Voice', None) is None or not self.__send_body['CgiRequest'][
                        'Voice']) and \
                    (self.__send_body['CgiRequest'].get('Images', None) is None or not self.__send_body['CgiRequest'][
                        'Images']) and \
                    (self.__send_body['CgiRequest'].get('ReplyTo', None) is None or not self.__send_body['CgiRequest'][
                        'ReplyTo']):
                self.__clear_()
                logger.error('消息发送失败, 消息不能为空')
                raise ValueError('消息不能为空')
        elif self.__send_body["CgiCmd"] == "PicUp.DataUp":
            self.__url = self.__upload_url

        if (resu := await asyncio.wait_for(asyncio.create_task(self.__request_http("POST",
                                                                                   url=self.__url,
                                                                                   headers=self.__headers,
                                                                                   json=self.__send_body)),
                                           10)) is None:
            self.__clear_()
        # 清空消息内容
        self.__clear_()
        self.__send_group = False
        return resu

    def __clear_(self):
        self.__tasks.clear()
        self.__send_body = {"CgiCmd": "MessageSvc.PbSendMsg", "CgiRequest": {"ToUin": '', "ToType": 0, "Content": ""}}

    @staticmethod
    def __verify_path(path: str):
        path = Path(path)
        if not path.exists():
            raise FileExistsError('文件不存在')
        if not path.is_file():
            raise ValueError('路径对应对象必须是一个文件')
        return path

    def __send(self, name, error_tips, send_body, _type, send_type, **kwargs):
        """
         照片可以发送多张, 即可同时多次.send_image
        :param file_path: 图片路径
        :param file_url: 图片链接
        :param file_base64: 图片 base64
        :return:
        """
        if not [ele for ele in kwargs.values() if ele is not None]:
            raise ValueError('必须有一个参数不为空')
        _data = {}

        for _key in list(kwargs.keys()):
            if (_data_dict := {ele[0]: ele[1] for ele in kwargs.items() if
                               ele[1] is not None}).get(_key, None) is not None and _data_dict[_key]:
                _data = {{'file_path': "FilePath", 'file_url': "FileUrl", 'file_base64': "Base64Buf"}[_key]: _data_dict[
                    _key]}
                break
        if not _data:
            raise ValueError("请确认参数是否合法, 参数不可以是空值")
        if (path := _data.get("filePath", None)) is not None:
            self.__verify_path(path)
        logger.info(f"发送{name}消息")

        @_catch_error(error_tips)
        async def _get_file_info():
            command_id = globals()[f'FRiEND_{_type.upper()}_COMMAND_ID']
            if self.__send_group:
                command_id = globals()[f'GROUP_{_type.upper()}_COMMAND_ID']
            json_data = {
                "CgiCmd": "PicUp.DataUp",
                "CgiRequest": {
                    "CommandId": command_id,
                    **_data
                }
            }
            print('json_data', json_data)
            resu = await self.__request_http("POST", url=self.__upload_url, headers=self.__headers, json=json_data)
            if self.__send_body['CgiRequest'].get(send_type, None) is None:
                self.__send_body['CgiRequest'][send_type] = []
            print(resu)
            if send_type in MULTIPLE_FILE:
                self.__send_body['CgiRequest'][send_type].append({
                    send_body: resu['ResponseData'][send_body],
                    "FileMd5": resu['ResponseData']['FileMd5'],
                    "FileSize": resu['ResponseData']['FileSize']
                })
            elif send_type in SINGLE_FILE:
                self.__send_body['CgiRequest'][send_type] = {
                    send_body: resu['ResponseData'][send_body],
                    "FileMd5": resu['ResponseData']['FileMd5'],
                    "FileSize": resu['ResponseData']['FileSize']
                }

        self.__tasks.append(_get_file_info)
        return self
