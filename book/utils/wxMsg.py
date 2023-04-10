# coding: utf-8
import hashlib
import time
import config

create_time = str(int(time.time()))


def unbind_email_msg(user_email):
    return f'''已经解绑邮箱:{user_email}\n 绑定邮箱：回复邮箱地址'''


def bind_email_msg(user_email):
    return f'''绑定邮箱:{user_email}\n 解除绑定回复:1001'''


no_book_content = "未找到书籍，在更新中！请换其他的书籍"
not_isbn_search = "不支持ISBN搜索，请输入书籍名称搜索！"
send_failed_msg = "根据其他用户报告，此书籍无法发送，请换一个编号继续！"
no_bind_email_msg = '''你还没有绑定邮箱！
请发送【邮箱地址】进行绑定
例如：book@book.com
查看帮助请回复 ？'''

send_to_kindle_help_url = 'https://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=2649877562&idx=1&sn=e3789377f9303432cb0a082ff81ad335&chksm=87c37ebdb0b4f7ab49168e70181efb9206434e0bb9b7620a8f17b258686f8faf70c696c9eb9d&token=305511071&lang=zh_CN#rd'
reply_help_msg = f'''<a href="{send_to_kindle_help_url}"> 发送到kindle手册 </a>
建议先发送到自己邮箱，然后自己转发kindle设备
回复：图书名称 搜索书籍
回复：邮箱地址 绑定邮箱
回复：email   查询邮箱
回复：1001    解绑邮箱
回复：1002    帮助手册
回复：1008    <a href="">英文杂志</a>
'''

reply_subscribe = f'''欢迎关注books图书馆，本书站收录图书超乎你的想象
按以下步骤将电子书自动发送到您的邮箱：

1.在聊天栏里发送邮箱地址 「你的邮箱地址」,如：xxxx@163.com
 
2.查询书籍，在聊天栏里发送你要找的书籍,直接回复书籍名称，如：平凡的世界
  
3.发送图书编号 1-15 ，静待5分钟邮箱收书。

如你还满意，请推荐给你的朋友。将是我改进的动力，🙏
直接发送kindle设备请查看<a href="{send_to_kindle_help_url}">帮助手册</a>
建议先发送到自己邮箱，然后自己转发kindle设备*
'''

donate_pic = 'http://mmbiz.qpic.cn/mmbiz' \
             '/6J0PjZVpchMmMZleHFZicHdbAGY4jXdOQH8Dy16lER8Im0VxU0pXS5E2xJf7Jn6icibPZticH3icBTvjg5icFscsxFNg/640' \
             '?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1 '


def mail_body(bookname):
    return f'''
    请查收附件！<br/>
    《{bookname}》<br/>
    ---------------------------------------------------<br/>
    <img src="{donate_pic}"  width="300" height="300" ><br/>
    ---------------------------------------------------<br/>
    欢迎你使用自助查询推送 kindle电子书 sendtokindles 公众号，我们竭诚为您服务。如果你有好的建议和意见，可以直接回复邮件！<br/>
    '''


def send_failed_body(bookname):
    return f'''
        《{bookname}》---发送失败！<br/>
        <p style="color:red"> 书籍下载失败 </p>
        请重新传查询，选择其他格式的图书接收！<br/>
        ---------------------------------------------------<br/>
        <img src="{donate_pic}"  width="300" height="300" ><br/>
        ---------------------------------------------------<br/>
        欢迎你使用自助查询推送 kindle电子书 sendtokindles 公众号，我们竭诚为您服务。如果你有好的建议和意见，可以直接回复邮件！<br/>
        '''


def mail_download_url_body(filename):
    """当文件大于20M的时候 发送下载地址到邮箱"""
    download_url = config.DOWNLOAD_URL + filename
    return f'''
        《{filename}》<br/>
        ---------------------------------------------------------<br/>
        |{filename}||<a href="{download_url}"> 下载地址 </a> <br/>
        下载链接地址有效期24个小时，请在有效期内下载。|<br/>
        ----------------------------------------------------------<br/>
        <img src="{donate_pic}"  width="300" height="300" ><br/>
        ----------------------------------------------------------<br/>
        欢迎你使用自助查询推送 kindle电子书 sendtokindles 公众号，我们竭诚为您服务。如果你有好的建议和意见，可以直接回复邮件！<br/>
        '''


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
    """微信校验签名"""
    temp_arr = [token, timestamp, nonce]
    temp_arr.sort()
    temp_str = ''.join(temp_arr)
    hash_str = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
    return hash_str == signature


def wx_reply_mail_msg(book_name, user_email):
    donate_url = 'https://mp.weixin.qq.com/s?__biz=MzA4NjU5OTY1Ng==&mid=401023694&idx=1&sn=9afeff751c06737c6c3c5de0faddc6a1#rd '
    return f'''《{book_name}》
已发送邮箱：{user_email} 
-------------注意-------------
当文件大于20M的时候 发送下载地址到邮箱！
文件发送有滞后，最好5分钟后查收，如无收到，请换一个编号重新申请发送！
------------------------------
           <a href="{donate_url}">☆ 打赏 ☆</a>
'''


def wx_reply_news(from_user, to_user):
    pic_url = 'https://mmbiz.qlogo.cn/mmbiz/6J0PjZVpchOuboUCtD8ia53mkkBicDnPNbXGTpHibHlEKBibBjQYAIWwOu30eiahwn1MuJGkWyXHNUU7SyJCibNRLMaQ/0?wx_fmt=jpeg'
    url = 'https://mp.weixin.qq.com/s/20zcsd3DYDUl7cpEWZwmDw'
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


def download_url(user_log):
    urls = ['https://ipfs.joaoleitao.org/ipfs/',
            'https://gateway.pinata.cloud/ipfs/',
            'https://cloudflare-ipfs.com/ipfs/',
            'https://hardbin.com/ipfs/']
    msg = ""
    for index, url in enumerate(urls, start=1):
        msg += f'<a href="{url}{user_log.ipfs_cid}?filename={user_log.book_name}">点击下载{index}</a>\n'
    return msg
