import hashlib
import re
import time, os

def unbind_email_msg(user_email):
    return f'''你好，你已经解绑邮箱:{user_email}\n解除绑定回复:1001'''
def bind_email_msg(user_email):
    return f'''你好，你绑定邮箱:{user_email}\n解除绑定回复:1001'''

no_book_content = "未找到书籍，在更新中！请换其他的书籍"

not_isbn_search = "不支持ISBN搜索，请输入书籍名称搜索！"

no_bind_email_msg = '''你好，你还没有绑定邮箱！
请发送【邮箱地址】进行绑定
例如：book@book.com
查看帮助请回复 ？'''

help_url = 'https://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=2649877534&idx=1&sn=ffd911121bd3e9e465acad01229aa862&chksm=87c37e99b0b4f78f49cdbe1bab4d7c5cdd0e927098a4f595d10623402955e02baa262df85799#rd'
reply_help_msg = f'''<a href="{help_url}"> 发送到kindle手册 </a>
回复：图书名称
回复：邮箱地址 绑定邮箱
回复：email 查询邮箱
回复：1001  解绑邮箱
回复：1002  帮助手册
'''

reply_subscribe = f'''hi，又一位热爱读书的朋友！
回复：图书名称 
回复：邮箱地址 绑定邮箱
回复：email 查询邮箱
回复：1001  解绑邮箱
回复：1002  帮助手册
而且通过这个公众号，电子书推送到Kindle上。
<a href="{help_url}">☆点击查看帮助☆</a>
'''
def mail_body(bookname):
    donate_pic = 'http://mmbiz.qpic.cn/mmbiz/6J0PjZVpchMmMZleHFZicHdbAGY4jXdOQH8Dy16lER8Im0VxU0pXS5E2xJf7Jn6icibPZticH3icBTvjg5icFscsxFNg/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1'
    weixin_pic = 'https://mmbiz.qlogo.cn/mmbiz/6J0PjZVpchNXHehVsRb4QvN2GPrq6LUlL3ibIZmfUaCPL6dL827IaVxudiazcicvbqBlDGZSyUBHyzicUe4A0rZEBQ/0'
    return f'''
    请查收附件！<br/>
    《{bookname}》<br/>
    ----------------------------------------------------------------------------<br/>
    <img src="{weixin_pic}" width="350" height="350">||<img src="{donate_pic}"  width="300" height="300" ><br/>
    ----------------------------------------------------------------------------<br/>
    欢迎你使用自助查询推送 kindle电子书 sendtokindles 公众号，我们竭诚为您服务。如果你有好的建议和意见，可以直接回复邮件！<br/>
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
def check_signature(token, signature, timestamp, nonce):
    """校验签名"""
    temp_arr = [token, timestamp, nonce]
    temp_arr.sort()
    temp_str = ''.join(temp_arr)
    hash_str = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
    return hash_str == signature
def wx_reply_mail_msg(book_name,user_email):
    donate_url = 'https://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=401023694&idx=1&sn=9afeff751c06737c6c3c5de0faddc6a1#rd'
    return f'''《{book_name}》已发送到邮箱：{user_email}请查收！
    
    <a href="{donate_url}">☆捐赠小二☆ </a>'''


def wx_reply_news(from_user,to_user):
    pic_url = 'https://mmbiz.qlogo.cn/mmbiz/6J0PjZVpchOuboUCtD8ia53mkkBicDnPNbXGTpHibHlEKBibBjQYAIWwOu30eiahwn1MuJGkWyXHNUU7SyJCibNRLMaQ/0?wx_fmt=jpeg'
    url = 'http://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=400901109&idx=1&sn=3d70499fe8efcb0a30aabce0e1f3d0f6#rd'
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