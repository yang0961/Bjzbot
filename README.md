# Bjzbot
不紧张Bot
基于OPQ的python sdk
## 目前完成部分功能，正在完成其他功能中
### Demo：
```py
# coding: utf-8
# @Author: 小杨大帅哥
from service import Register
from message import Message
from sender import Account
res = Register()


@res.message_register(isDivision=True, isGroup=True)
async def _(acc: Account, msg: Message):
    if not msg.isUsefulMsg:
        return None
    # 发送文字 + 照片 给群组
    await acc.send_content("你好").send_image("demo.png").to_group(msg.groupId)
    # 群内 at对方
    await acc.send_content("你好").at(msg.senderId).to_group(msg.groupId)
    # 回复消息
    await acc.send_content("我正在回复你啊").send_msg_reply(**msg.getReplyParams, replay_sender_id=msg.senderId).to_group(msg.groupId)
    # 发送语音
    await acc.send_voice("demo.mp3").to_group(msg.groupId)
    # 指定获取群组成员
    async for item in acc.get_group_members(msg.groupId):
        print(item)

res.run(print_msg=False, thread_proces_msg=True)


```
## 功能：


* 获取框架信息
```py
await acc.get_self_info()
```

* 发送照片
```py
# 多文件
await acc.send_image(filep_path=["demo.py"]).to_group(groupId)
# 单文件
await acc.send_image(filep_path="demo.py").to_group(groupId)
```

* 发送文字
```py
await acc.send_content("demo").to_group(groupId)
```

* 发送语音
```py
await acc.send_voice("demo.mp3").to_group(groupId)
```

* 发送群json卡片
```py
await acc.send_group_json("json数据").to_group(groupId)
```

* 发送文字和照片的组合消息
```py
await acc.send_content("demo").send_image(filep_path="demo.py").to_group(groupId)
```

* 发送 at消息, 只用于群聊
```py
await acc.send_content("demo").at(userId).to_group(groupId)
```

* 回复消息
```py
await acc.send_content("回复").send_msg_reply("demo").to_group(groupId)
```

* 获取群成员
```py
# 每次最多获取500人
async for member in acc.get_group_members(groupId):
    print(member)
```

* 发送好友, 私聊, 群组
```py
# 只需要在每个send操作最后
.to_group(groupId) # 推送消息给群组
.to_friend(friendId) # 推送消息给好友
.to_private(private_id, group_id) # 推送给私聊群内成员
```

