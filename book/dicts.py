# coding: utf-8

# 发送邮件状态

class SEND_STATUS:
    WAITING = 0   # 等待发送
    SUCCESS = 1  # 成功
    FAILED = 3  # 失败
    UNKONOW = 4    # 晚上重新发送一次