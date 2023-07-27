import time
from datetime import datetime, timedelta
import datetime as dt

def get_now():
    return datetime.now()


def utc_to_local(utc_time, fmt='%Y-%m-%d %H:%M:%S', tz=8):
    if not utc_time:
        return None
    if not isinstance(utc_time, datetime):
        utc_time = str_to_dt(utc_time)
    # 将UTC时间转换为本地时间
    return dt_to_str(utc_time + timedelta(hours=int(tz)))


def get_days_later(days):
    # 获取当前时间
    now = datetime.utcnow()
    # 计算30天后的日期
    after_days = now + timedelta(days=days)
    # 返回30天后的日期
    return after_days.strftime('%Y-%m-%d %H:%M:%S')


def str_to_dt(time_str, fmt='%Y-%m-%d %H:%M:%S'):
    """
    自动识别时间字符串格式，并转换为 datetime 类型
    Args: time_str: 时间字符串，可以是各种格式
    Returns: datetime 对象
    """
    if time_str is None:
        return None
    try:
        time_dt = datetime.strptime(time_str, fmt)
    except ValueError:
        try:
            time_dt = datetime.strptime(time_str, '%Y-%m-%d')
        except ValueError:
            from dateutil import parser
            time_dt = parser.parse(time_str)
    return time_dt


def dt_to_str(time_dt) -> str:
    if isinstance(time_dt, datetime):
        return time_dt.strftime('%Y-%m-%d %H:%M:%S')
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


if __name__ == "__main__":
    days = -30
    now = "Fri, 31 Mar 2023 00:00:51 +0800"
    print(type(utc_to_local(now)))
    print(10 + days)
