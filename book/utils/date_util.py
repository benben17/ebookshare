import time
from datetime import datetime, timedelta
import datetime as dt

dateFullFmt = '%Y-%m-%d %H:%M:%S'
dateFmt = '%Y-%m-%d'


def get_now():
    return datetime.now()


def utc_to_local(utc_time_str, utc_fmt=dateFullFmt, local_fmt=dateFullFmt, tz=8):
    """
    UTC时间转本地时间
    :param utc_time_str: UTC时间字符串
    :param utc_fmt: UTC时间格式
    :param tz: 时区
    :param local_fmt: 本地时间格式
    :return: 本地时间字符串
    """


def get_days_later(days):
    # 获取当前时间
    now = datetime.utcnow()
    # 计算30天后的日期
    after_days = now + timedelta(days=days)
    # 返回30天后的日期
    return after_days.strftime(dateFullFmt)


def str_to_dt(time_str, fmt=dateFullFmt):
    """
    Args: time_str: 时间字符串，可以是各种格式
    Returns: datetime 对象
    """
    if time_str is None:
        return None
    try:
        time_dt = datetime.strptime(time_str, fmt)
    except ValueError:
        try:
            time_dt = datetime.strptime(time_str, dateFmt)
        except ValueError:
            from dateutil import parser
            time_dt = parser.parse(time_str)
    return time_dt


def dt_to_str(time_dt, fmt=dateFullFmt) -> str:
    """
    :param time_dt:
    :type fmt: object
    """
    if isinstance(time_dt, datetime):
        return time_dt.strftime(fmt)
    else:
        return time_dt


def format_time(d_t) -> str:
    if d_t is None:
        return None
    if isinstance(d_t, datetime):
        return dt_to_str(d_t)
    else:
        return dt_to_str(str_to_dt(d_t))


def now_datetime() -> str:
    return str(dt.datetime.fromtimestamp(int(time.time())))


def now_date() -> str:
    return str(datetime.date.today())


def timestamp() -> int:
    return int(time.time())


def long_timestamp() -> str:
    return str(time.time()).replace(".", "")


def timestamp_to_date(timestamp: int) -> str:
    """
    timestamp to date
    allow timestamp is int or string
    convert failed return None
    check convert date is correct
    """
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    if isinstance(timestamp, int):
        try:
            return time.strftime(dateFullFmt, time.localtime(timestamp))
        except ValueError:
            return None
    return None


def date_to_timestamp(time_dt) -> int:
    """
    date to timestamp
    check date is string or datetime
    allow all date format
    convert failed return None
    """
    if isinstance(time_dt, str):
        time_dt = str_to_dt(time_dt)
    if isinstance(time_dt, datetime):
        return int(time.mktime(time_dt.timetuple()))
    return None


if __name__ == "__main__":
    days = -30
    now = "Fri, 31 Mar 2023 00:00:51 +0800"
    # print(type(utc_to_local(now)))
    print(timestamp_to_date("16801920511000"))
