import time
from datetime import datetime, timedelta

import pytz


def utc_to_local(utc_time):
    # 获取本地时区信息
    local_tz = pytz.timezone('Asia/Shanghai')
    # 将UTC时间转换为本地时间
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    # 输出本地时间
    return local_time.strftime('%Y-%m-%d %H:%M:%S')


def get_days_later(days):
    # 获取当前时间
    now = datetime.utcnow()
    # 计算30天后的日期
    after_days = now + timedelta(days=days)
    # 返回30天后的日期
    return after_days.strftime('%Y-%m-%d %H:%M:%S')


def str_to_dt(time_str):
    """
    自动识别时间字符串格式，并转换为 datetime 类型
    Args: time_str: 时间字符串，可以是各种格式
    Returns: datetime 对象
    """
    try:
        time_dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            time_dt = datetime.strptime(time_str, '%Y-%m-%d')
        except ValueError:
            from dateutil import parser
            time_dt = parser.parse(time_str)
    return time_dt


def dt_to_str(time_dt):
    if isinstance(time_dt, datetime):
        return time_dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return time_dt


def now_datetime() -> str:
    return str(datetime.datetime.fromtimestamp(int(time.time())))


def now_date() -> str:
    return str(datetime.date.today())


def timestamp() -> int:
    return int(time.time())


def long_timestamp() -> str:
    return str(time.time()).replace(".", "")


if __name__ == "__main__":
    days = -30
    now = "Fri, 31 Mar 2023 00:00:51 +0800"
    print(str_to_dt(now))
    print(10 + days)
