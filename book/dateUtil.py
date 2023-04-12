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
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')


def dt_to_str(time_dt):
    return time_dt.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    days = -30

    print(10+days)

