import json
import logging

from flask import redirect, send_from_directory, request, Blueprint
from sqlalchemy import or_
from book import cache, db, upgradeUser, User
from book.dicts import SEND_STATUS
from book.utils import *
from book.utils.wxMsg import *

blueprint = Blueprint(
    get_file_name(__file__),
    __name__,
    url_prefix='/api'
)


@blueprint.route('/wechat', methods=['GET', 'POST'])
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
        from book.models import User, Userlog
        # 处理消息请求
        msg_type, from_user, to_user, content, event = parse_xml(request.data)
        from_user = from_user.strip()
        # logging.error(from_user)
        to_user = to_user.strip()
        if msg_type.strip() == 'event' and event.strip() == 'subscribe':
            return wx_reply_xml(from_user, to_user, reply_subscribe)
        elif msg_type.strip() == 'text':
            content = content.strip()
            # 查询用户
            if content.lower() in help_msg:
                return wx_reply_xml(from_user, to_user, reply_help_msg)
            elif content == '1002':
                return wx_reply_news(from_user, to_user)
            # 查找用户信息
            user = User.query.filter(User.wx_openid == from_user).first()
            # 查询绑定的邮箱地址
            if content.lower() in email_help:
                if not user.kindle_email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                return wx_reply_xml(from_user, to_user, bind_email_msg(user.kindle_email))
            # 解绑
            if content == '1001':
                user_email = user.kindle_email
                if not user_email:
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                user.kindle_email = ""
                db.session.add(user)
                db.session.commit()
                return wx_reply_xml(from_user, to_user, unbind_email_msg(user_email))
            if content == '1008':
                return wx_reply_xml(from_user, to_user, news_feed())
            # 绑定邮箱
            if check_email(content):
                if user:
                    if not user.kindle_email:
                        logging.info("if user.kindle_email:")
                        user.name = content.split("@")[0]
                        user.email = content
                        user.kindle_email = content
                        db.session.add(user)
                        db.session.commit()
                    return wx_reply_xml(from_user, to_user, bind_email_msg(user.kindle_email))
                else:  # 通过openID 没有查询到用户
                    user = User.query.filter(User.kindle_email == content).first()
                    logging.info("User.query.filter(User.kindle_email == content).first()")
                    if user:
                        if not user.wx_openid:
                            user.wx_openid = from_user
                            db.session.add(user)
                    else:
                        user = User(name=content.split("@")[0], email=content, kindle_email=content, wx_openid=from_user, id=gen_userid())
                        db.session.add(user)
                    db.session.commit()
                    logging.info(user.kindle_email)
                    # logging.info("-------")
                    return wx_reply_xml(from_user, to_user, bind_email_msg(user.kindle_email))
            # 检查是不是 书籍ISBN
            if content.replace("-", "").isdigit() and is_isbn(content):
                msg_content, books_cache = search_net_book(isbn=content, openid=from_user)
                if books_cache is not None:
                    cache.set_many(books_cache)  # 存缓存
                return wx_reply_xml(from_user, to_user, msg_content)

            if from_user == 'o6MX5t3TLA6Un9Mw7mM3nHGdOI-s':
                if content.startswith("upgrade") or content.startswith("refund"):
                    info = content.split(":")
                    if len(info) == 3:
                        if upgradeUser.upgrade_user_thread(type=info[0],user_name=info[1], p_name=info[2]):
                            return wx_reply_xml(from_user, to_user, f"{info[1]}:用户升级中.....")
                    return wx_reply_xml(from_user, to_user, "未找到用户，或者信息错误")

            # 发送文件
            if re.match("[0-9]", content) and int(content) <= 16:
                # 每个用户每天最多下载5本书
                if not user or not user.kindle_email:  # 必须绑定邮箱
                    return wx_reply_xml(from_user, to_user, no_bind_email_msg)
                usersend = Userlog.query.filter(Userlog.wx_openid == from_user, Userlog.status == 1,
                                                Userlog.create_time > get_ymd_dt()).all()
                if len(usersend) > 6:
                    wx_reply_xml(from_user, to_user, "今天已经下载5本书，请明天在进行发送！")
                book_info = cache.get(f'{from_user}_{content}')
                if book_info is not None:
                    send_info = book_info.split(":")
                    user_log = Userlog(wx_openid=from_user, book_name=send_info[0],
                                       receive_email=user.kindle_email, user_id=user.id,
                                       operation_type='download', status=SEND_STATUS.WAITING, ipfs_cid=send_info[1],
                                       filesize=send_info[2])
                    db.session.add(user_log)
                    db.session.commit()
                    return wx_reply_xml(from_user, to_user,
                                        wx_reply_mail_msg(send_info[0], user.kindle_email) + download_url(user_log))
                else:
                    return wx_reply_xml(from_user, to_user, ''' 请重新搜索书籍 \n'''+reply_help_msg)
            # 搜索 图书
            msg_content, books_cache = search_net_book(title=content, openid=from_user)
            if books_cache is not None:
                cache.set_many(books_cache)  # 存缓存
            return wx_reply_xml(from_user, to_user, msg_content)

        else:  # 其他未知消息
            return wx_reply_xml(from_user, to_user, reply_help_msg)

@blueprint.route('/download/<path:filename>')
def dl_file(filename):
    if os.path.exists(os.path.join(config.DOWNLOAD_DIR, filename)) is False:
        return redirect("/404")
    return send_from_directory(config.DOWNLOAD_DIR, filename)
    # return APIResponse.success(data="欢迎关注 sendtokindles 公众号下载电子书")
