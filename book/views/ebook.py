import logging
from flask import request, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from book.utils import get_file_name
from book.utils.ApiResponse import APIResponse
from book.dbModels import Userlog, db

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2')
@blueprint.route("/send/ebook", methods=["POST"])
@jwt_required()
def dl_ebook():
    try:
        data = request.get_json()
        book_name = data.get('book_name')
        ipfs_cid = data.get('ipfs_cid')
        if not all(x in data for x in ['book_name', 'ipfs_cid']):
            return APIResponse.internal_server_error(msg="参数错误！")
        user = get_jwt_identity()
        if user.wx_openid is None:
            return APIResponse.bad_request(msg="请先关注公众号，发送注册邮箱进行绑定")

        filesize = data.get('filesize', 0)
        user_log = Userlog(wx_openid=user.wx_openid, book_name=book_name, receive_email=user.kindle_email,
                           user_id=user.id, operation_type='download',
                           status=0, ipfs_cid=ipfs_cid, filesize=filesize)
        db.session.add(user_log)
        db.session.commit()
        return APIResponse.success(msg="发送成功，邮箱接收！")

    except Exception as e:
        logging.error(e)
        return APIResponse.bad_request(msg="发送失败")
