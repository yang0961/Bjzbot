# coding: utf-8
# @Author: 小杨大帅哥


def load_fn(msg):
    msg.isGroup = isGroup
    msg.isBot = isBot
    msg.botAccount = botAccount
    msg.text = text
    msg.groupId = groupId
    msg.senderId = senderId
    msg.havingImage = havingImage
    msg.getImage = getImage
    msg.getVideo = getVideo
    msg.getVoice = getVoice
    msg.is_at = is_at
    msg.getReplyParams = getReplyParams
    msg.isUsefulMsg = isUsefulMsg
    msg.getGroupInfo = getGroupInfo
    return msg


def _catch_error(_return=None):
    def _catch(func):
        def __catch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                return _return
        return __catch
    return _catch


@property
@_catch_error(False)
def isGroup(self):
    if str(self.CurrentPacket.EventData.MsgHead.FromType) == '2' and \
            "GROUP" in self.CurrentPacket.EventName:
        return True
    return False


@property
@_catch_error(None)
def isBot(self):
    return str(self.CurrentPacket.EventData.MsgHead.SenderUin) == str(self.CurrentQQ)


@property
@_catch_error(None)
def botAccount(self):
    return int(self.CurrentQQ)


@property
@_catch_error(None)
def text(self):
    if not self.isUsefulMsg:
        return None
    return self.CurrentPacket.EventData.MsgBody.Content


@property
@_catch_error(None)
def groupId(self):
    if not self.isGroup:
        return None
    return int(self.CurrentPacket.EventData.MsgHead.FromUin)


@property
@_catch_error(None)
def senderId(self):
    return int(self.CurrentPacket.EventData.MsgHead.SenderUin)

@property
@_catch_error(False)
def isUsefulMsg(self):
    if self.CurrentPacket.EventData.MsgBody is None or self.CurrentPacket.EventData.MsgHead is None:
        return False
    return True

@property
@_catch_error(False)
def havingImage(self):
    if not self.isUsefulMsg:
        return False
    return isinstance(self.CurrentPacket.EventData.MsgBody.Images, list)


@property
@_catch_error(None)
def getImage(self):
    if not self.havingImage:
        return None
    return self.CurrentPacket.EventData.MsgBody.Images


@property
@_catch_error(None)
def getVideo(self):
    if not self.isUsefulMsg:
        return None
    return self.CurrentPacket.EventData.MsgBody.Video


@property
@_catch_error(None)
def getGroupInfo(self):
    if not self.isUsefulMsg and not self.isGroup:
        return None
    return self.CurrentPacket.EventData.MsgHead.GroupInfo

@property
@_catch_error(None)
def getReplyParams(self):
    if not isUsefulMsg:
        return None
    if (msg := self.CurrentPacket.EventData.MsgHead) is None:
        return None
    return {"msg_seq": int(msg.MsgSeq), "msg_time": int(msg.MsgTime), "msg_uid": int(msg.MsgUid)}


@property
@_catch_error(None)
def getVoice(self):
    if not self.isUsefulMsg:
        return None
    return self.CurrentPacket.EventData.MsgBody.Voice


@_catch_error(False)
def is_at(self, include_at_all=True):
    if not self.isUsefulMsg:
        return False
    if (msg := self.CurrentPacket.EventData.MsgBody).AtUinLists is None:
        return False
    if not include_at_all:
        return len(set([ele.Uin for ele in msg.AtUinLists if str(ele.Uin) == str(self.CurrentQQ)])) == 1
    return len(set([ele.Uin for ele in msg.AtUinLists if str(ele.Uin) == str(self.CurrentQQ) or ele.Uin == 0])) == 1
