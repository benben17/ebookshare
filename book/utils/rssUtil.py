import logging

import feedparser
import requests

import config
from book.utils import get_rss_host


def is_rss_feed(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        print(feed.get('version'))
        if feed.get('version'):
            return True
    except:
        pass
    return False


def get_rss_latest_titles(rss_url, num):
    """
    获取一个 RSS 源的最新 n 篇文章的 title。
    """
    try:
        titles = []
        d = feedparser.parse(rss_url)
        for entry in d.entries[:int(num)]:
            if entry.title:
                titles.append(entry.title)
            # print(entry.title)
        return titles
    except Exception as e:
        logging.error(e)



rss_list = [
    # ('News','FT - World', 'https://www.ft.com/world?format=rss'),
    # ('News','FT - US', 'https://www.ft.com/us?format=rss'),
    # ('News','FT - Companies', 'https://www.ft.com/companies?format=rss'),
    # ('News','FT - Tech', 'https://www.ft.com/technology?format=rss'),
    # ('News','FT - Markets', 'https://www.ft.com/markets?format=rss'),
    # ('News','FT - Opinion', 'https://www.ft.com/opinion?format=rss'),
    # ('News','FT - Life & Arts', 'https://www.ft.com/life-arts?format=rss'),
    ('Business','FX Markets - Trading','https://rsshub.app/fx-markets/trading'),
    ('Business','FX Markets - Infrastructure','https://rsshub.app/fx-markets/infrastructure'),
    ('Business','FX Markets - Tech & Data','https://rsshub.app/fx-markets/tech-and-data'),
    ('Business','FX Markets - Infrastructure','https://rsshub.app/fx-markets/Regulation')
]



if __name__ == "__main__":
    # print(get_rss_latest_titles('https://www.ft.com/world?format=rss', 10))
    d = feedparser.parse("https://feedx.net/rss/economistp.xml")
    # print(len(d))
    print(d.entries[0])
    # for rss in rss_list:
    #     path = '/api/v2/rss/manager'
    #     data = {'key': config.RSS2EBOOK_KEY,
    #             'user_name': 'admin',
    #             'creator': 'admin',
    #             "title": rss[1],
    #             "url": rss[2],
    #             "is_fulltext": "flase",
    #             "category": rss[0],
    #             "librss_id": 1
    #             }
    #     print(data)
    # #     # request_url = "http://127.0.0.1:8080"
    #     res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS, timeout=60)
    #     # print(rss)
    #     print(res.text, res.status_code)