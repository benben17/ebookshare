import datetime
import json
import logging
from book import request, cache, app, db, Blueprint
from book.wxMsg import *
from book.utils import *
# wx = Blueprint('wx', __name__)

@app.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 处理验证请求
        token = config.wechat_token
        echostr = request.args.get('echostr', '')
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        return echostr if check_signature(token, signature, timestamp, nonce) else ''

    elif request.method == 'POST':
        from book.dbModels import User, Userlog, Books
        # 处理消息请求
        msg_type, from_user, to_user, content, event = parse_xml(request.data)
        from_user = from_user.strip()
        logging.error(from_user)
        to_user = to_user.strip()
        if msg_type.strip() == 'event' and event.strip() == 'subscribe':
            return wx_reply_xml(from_user, to_user, reply_subscribe)
        elif msg_type.strip() == 'text':
            content = content.strip()
            # 查询用户
            if content.lower() in ['?', 'h', 'help', '帮助', '？']:
                return wx_reply_xml(from_user, to_user, reply_help_msg)
            elif content == '1002':
                return wx_reply_news(from_user, to_user)
            # 查找用户信息
            user = User.query.filter(User.wx_openid == from_user).first()
            if user is None:
                user = User(wx_openid=from_user)
                db.session.add(user)
                db.session.commit()
            # 查询绑定的邮箱地址
            if content.lower() == "email":
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
            # 解绑
            if content == '1001':
                user_email = user.email
                if not user_email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                user.email = ""
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, unbind_email_msg(user_email))

            # 绑定邮箱
            if checkemail(content):
                if user.email:
                    return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))
                user.email = content
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.email))

            if check_isbn(content):
                msg_content, books_cache = search_net_book(isbn=content, openid=from_user)
                if books_cache is not None:
                    cache.set_many(books_cache)  # 存缓存
                return wx_reply_xml(from_user, to_user, msg_content)
            # if content == 'next':

            if content == "哈哈哈":
                return wx_reply_news(from_user, to_user)
            # 发送文件
            if re.match("[0-9]", content) and int(content) <= 16:
                if not user.email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                # 每个用户每天最多下载5本书
                usersend = Userlog.query.filter(Userlog.wx_openid == from_user, Userlog.status == 1,
                                                Userlog.create_time > get_now_date()).all()
                if len(usersend) > 5:
                    wx_reply_xml(from_user, to_user, "今天已经下载5本书，请明天在进行发送！")

                book_info = cache.get(f'{from_user}_{content}')
                if book_info is not None:
                    send_info = book_info.split(":")
                    logging.error(send_info)
                    # 之前是否发送失败过，如果失败则返回此书籍不可用
                    userlog = Userlog.query.filter(Userlog.book_name == send_info[0],Userlog.ipfs_cid == send_info[1],Userlog.status == config.FAILED_FlAG).all()
                    if userlog:
                        return wx_reply_xml(from_user, to_user, send_failed_msg)
                    user_log = Userlog(wx_openid=user.wx_openid, book_name=send_info[0], receive_email=user.email,
                                       operation_type='download', status=0, ipfs_cid=send_info[1],filesize=send_info[2])
                    db.session.add(user_log)
                    db.session.commit()
                    return wx_reply_xml(from_user, to_user, wx_reply_mail_msg(send_info[0], user.email))

                else:
                    return wx_reply_xml(from_user, to_user, reply_help_msg)

            # 搜索 图书
            msg_content, books_cache = search_net_book(title=content, openid=from_user)
            if books_cache is not None:
                cache.set_many(books_cache) #存缓存
            return wx_reply_xml(from_user, to_user, msg_content)

        else: # 其他未知消息
            return wx_reply_xml(from_user, to_user, reply_help_msg)


class WeChat:
    def __init__(self):
        self.APPID = config.APPID
        self.APPSECRET= config.APPSECRET

    def get_token(self):

        token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'
        try:
            res = requests.get(token_url.format(self.APPID,self.APPSECRET))
            json_res = json.loads(res.text)
            if 'access_token' in json_res:
                # cache.add('access_token',json_res['access_token'])
                return json_res['access_token']
        except Exception as e:
            logging.error("获取token 失败！："+e)
    def create_menu(self):
        ACCESS_TOKEN = self.get_token()
        create_menu_button_url= f'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={ACCESS_TOKEN}'
        my = "http://www.baidu.com"
        param = '''{
            "button": [
                {
                    "type": "click",
                    "name": "个人中心",
                    "key": "{my}"
                },
                {
                    "name": "菜单",
                    "sub_button": [
                        {
                            "type": "view",
                            "name": "搜索",
                            "url": "http://www.soso.com/"
                        },
                        {
                            "type": "click",
                            "name": "赞一下我们",
                            "key": "V1001_GOOD"
                        }]
                }]
        }'''
        param.format(my)
        requests.post(create_menu_button_url,param)

        try:
            print("a")
        except Exception as e:
            print(e)
if __name__ == '__main__':
    print(str(int(time.time())))