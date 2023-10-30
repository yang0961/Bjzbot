# coding: utf-8
# @Author: 小杨大帅哥
from service import Register
from message import Message
from sender import Account
res = Register()


@res.message_register(isDivision=False)
async def _(acc: Account, msg: Message):
    if msg.senderId != msg.botAccount and msg.isGroup:
        return None
    # 发送文字 + 照片 给群组
    await acc.send_content("你好").send_image("demo.png").to_group(msg.groupId)
    # 回复消息
    await acc.send_content("我正在回复你啊").send_msg_reply(**msg.getReplyParams, replay_sender_id=msg.senderId).to_group(msg.groupId)
    # 指定获取群组成员
    async for item in acc.get_group_members(msg.groupId):
        print(item)

res.run(print_msg=False, thread_proces_msg=True)

