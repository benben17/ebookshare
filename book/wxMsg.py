import re
import time, os

no_bind_email_msg = '''你好，你还没有绑定邮箱！
请发送【邮箱地址】进行绑定
例如：book@book.com\n'''
help_url = 'https://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=2649877534&idx=1&sn=ffd911121bd3e9e465acad01229aa862&chksm=87c37e99b0b4f78f49cdbe1bab4d7c5cdd0e927098a4f595d10623402955e02baa262df85799#rd'
reply_help = f'''<a href="{help_url}"> 发送到kindle手册 </a>
回复：图书名称
回复：邮箱地址 绑定邮箱
回复：email 查询邮箱
回复：1001  解绑邮箱
回复：1002  帮助手册
'''

reply_subscribe = f'''hi，又一位热爱读书的朋友！
读书推荐
而且通过这个公众号，电子书推送到Kindle上。
<a href="{help_url}">☆点击查看帮助☆</a>

'''
def mail_body(bookname):
    return f'''
    请查收附件！《{bookname}》
    ----------------------------------------------------------------------------<br/>
    <img src=\"https://mmbiz.qlogo.cn/mmbiz/6J0PjZVpchNXHehVsRb4QvN2GPrq6LUlL3ibIZmfUaCPL6dL827IaVxudiazcicvbqBlDGZSyUBHyzicUe4A0rZEBQ/0\" /><br/>
    欢迎你使用自助查询推送 kindle电子书 sendtokindles 微信号，我们竭诚为您服务。如果你有好的建议和意见，可以直接回复邮件！<br/>
    '''

def checkemail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.findall(pattern, email):
        return True
    else:
        return False

create_time = str(int(time.time()))
def wx_reply_xml(from_user, to_user, msg_content):
    """
    desc: 微信回复消息模版
    :param from_user: 发送人
    :param to_user: 接受人
    :param msg_content: 接收消息内容
    :return:
    """

    return f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{create_time}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{msg_content}]]></Content>
        </xml>
        """


pic_url = 'https://mmbiz.qlogo.cn/mmbiz/6J0PjZVpchOuboUCtD8ia53mkkBicDnPNbXGTpHibHlEKBibBjQYAIWwOu30eiahwn1MuJGkWyXHNUU7SyJCibNRLMaQ/0?wx_fmt=jpeg'
url = 'http://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=400901109&idx=1&sn=3d70499fe8efcb0a30aabce0e1f3d0f6#rd'

def wx_reply_news(from_user,to_user):
    news_title = '发送到kindle手册'
    return f'''<xml>
          <ToUserName><![CDATA[{from_user}]]></ToUserName>
          <FromUserName><![CDATA[{to_user}]]></FromUserName>
          <CreateTime>{create_time}</CreateTime>
          <MsgType><![CDATA[news]]></MsgType>
          <ArticleCount>1</ArticleCount>
          <Articles>
            <item>
              <Title><![CDATA[{news_title}]]></Title>
              <Description><![CDATA[{news_title}]]></Description>
              <PicUrl><![CDATA[{pic_url}]]></PicUrl>
              <Url><![CDATA[{url}]]></Url>
            </item>
          </Articles>
        </xml>
        '''