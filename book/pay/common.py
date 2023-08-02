# 导入支付基类
import datetime
import hashlib
import json
import logging
import os
from datetime import datetime
from random import random
from urllib import parse

from book.utils.commUtil import cacheKey


# from Crypto.PublicKey import RSA
# from Crypto.Signature import PKCS1_v1_5
# from Crypto.Hash import SHA256


def get_order_no():
    time = datetime.now()
    random_num = random.randint(100, 999)
    return datetime.strftime(time, "%Y%m%d%H%M%S") + str(random_num)


# def rsa_verify_sign(data_str, sign, secret_key, key_is_file=False, need_import=False):
#     """
#     :param data_str: 等待验签的数据
#     :param sign: 数据的签名
#     :param secret_key: 秘钥
#     :param key_is_file: 秘钥是否是一个文件目录
#     :param need_import: 是否需要预导入秘钥
#     :return:
#     """
#     secret_key = get_secret(secret_key, key_is_file, need_import)
#     signer = PKCS1_v1_5.new(secret_key)
#     digest = SHA256.new()
#     digest.update(data_str.encode("utf8"))
#     if signer.verify(digest, base64.decodebytes(sign.encode("utf8"))):
#         return True
#     return False


# def get_secret(secret_key, key_is_file=False, need_import=False):
#     """
#     :param secret_key: 秘钥、或者秘钥路径
#     :param key_is_file: 标识秘钥是否是一个文件
#     :param need_import: 是否需要做导入处理
#     :return: 秘钥
#     """
#     res = secret_key
#     if secret_key:
#         if key_is_file:
#             res = read_secret(secret_key)
#         else:
#             if need_import:
#                 res = RSA.importKey(secret_key)
#
#     return res


# def read_secret(secret_path, import_key=True):
#     """
#     从文件加载秘钥
#     :param secret_path:
#     :param import_key: 是否需要导入秘钥
#     :return:
#     """
#     with open(secret_path, "r") as fp:
#         return RSA.importKey(fp.read()) if import_key else fp.read()
#

# def rsa_sign(unsigned_string, secret_key, key_is_file=False, need_import=False) -> str:
#     """
#     RSA数字签名协议根据PKCS#1 v1.5
#     :param unsigned_string: 等待签名的字符串
#     :param secret_key: 秘钥
#     :param need_import: 如果为True, 则初始化秘钥
#     :param key_is_file: 为True 表示需要从文件读取
#     :return: 将签名base64编码
#     """
#     if unsigned_string and secret_key:
#         if key_is_file:
#             secret_key = read_secret(secret_key)
#         else:
#             if need_import:
#                 secret_key = RSA.importKey(secret_key)
#         # 创建一个签名对象
#         signer = PKCS1_v1_5.new(secret_key)
#         # 签名
#         signature = signer.sign(SHA256.new(unsigned_string))
#         # base64 编码，转换为unicode表示并移除回车
#         sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
#         return sign
#     return ''


def join_tuple_param(data: list, quote_plus=False) -> str:
    """
    :param data:  [(key, value), (key2, value2)]
    :param quote_plus: 对于key、value中出现了&、=之类的符号会进行编码
    :return: key=value&key2=value2
    """
    if isinstance(data, list):
        if quote_plus:
            return "&".join("{0}={1}".format(k, parse.quote_plus(v)) for k, v in data)
        return "&".join("{0}={1}".format(k, v) for k, v in data)
    return ''


def join_tuple_param_alipay(data: list) -> str:
    """
    :param data:  [(key, value), (key2, value2)]
    :return: key=value&key2=value2
    """
    if isinstance(data, list):
        return "{" + ",".join('"{0}":"{1}"'.format(k, v.replace('/', '\/')) for k, v in data) + "}"
    return ''


def ordered_dict(data: dict) -> []:
    """
    将字典排队
    :param data: 字典
    :return: [(key, value), (key2, value2)]
    """
    if isinstance(data, dict):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)
        # 将字典类型的数据dump出来
        for key in complex_keys:
            # for k, v in data[key].items():
            data[key] = json.dumps(data[key], separators=(',', ':'))
        return sorted([(k, v) for k, v in data.items()])
    return []


# def generate_qr_code(url: str) -> str:
#     """
#     创建一个二维码
#     :param url: 二维码url
#     :return: base64编码的图片
#     """
#     try:
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=12,
#             border=0.1,
#         )
#         qr.make(fit=True)
#         qr.add_data(url)
#         img = qr.make_image(fill_color="white", back_color="#000000")
#         buf = io.BytesIO()
#         img.save(buf, format='PNG')
#         return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
#     except Exception as e:
#         logging.error('二维码生成错误%s' % e)
#         return ''


def sign_md5(msg: bytes) -> str:
    """
    将传递的字节数据签名
    :param msg:
    :return:
    """
    if isinstance(msg, bytes):
        m = hashlib.md5()
        m.update(msg)
        return m.hexdigest()
    return ''


# def xml_to_dict(xml_str: str) -> dict:
#     data_orderedD = xmltodict.parse(xml_str)
#     return json.loads(json.dumps(data_orderedD, indent=4))
#
#
# def dicttoxml(dict_data: dict) -> str:
#     return xmltodict.unparse(dict_data, pretty=True, encoding='utf-8')


class Dict(dict):
    """
    使字典可以属性方式访问值
    """

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, key, value):
        self[key] = value


def catch_error(func):
    """
    捕获函数运行异常装饰器
    :param func:
    :return:
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{func.__qualname__} 发生异常 {e}")
            return dict(code=-1, msg='接口内部发生异常', data=None)

    return inner


def param_diff(param: [dict, list], _in: [dict, list]):
    """
    检查 _in 是否包含了 param中的所有项
    如果传递的是 dict 会将它们的key转换为一个集合，并使用集合的 difference 方法判断差集来实现
    :param param:
    :param _in:
    :return:
    """
    if isinstance(param, dict):
        param = set(param.keys())
    if isinstance(_in, dict):
        _in = set(_in.keys())
    return list(set(param).difference(set(_in)))


def get_res(code=0, msg='success', data=None) -> dict:

    return dict(code=code, msg=msg, data=data)


def file_base_name(abs_path: str) -> str:
    return os.path.basename(abs_path)


if __name__ == '__main__':
    need = ["name", "age", "hobby", "sex"]
    args = {"name": 1, "age": 2, "hobby": 1, "sex": 1}
    print(param_diff(need, args))
    # print({1,2,3}.difference({1,2}) )
