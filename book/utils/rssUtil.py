import logging
import uuid

import feedparser
import requests

import config
from book.dateUtil import dt_to_str, str_to_dt
from book.utils import get_rss_host, gen_userid
from book.utils.commUtil import new_passwd


def is_rss_feed(rss_url):
    try:
        if not rss_url.startswith('http'):
            rss_url = 'http://'+rss_url
        feed = feedparser.parse(rss_url)
        # print(feed.get('version'))
        if feed.get('version'):
            return True
    except:
        pass
    return False


def get_rss_latest_titles(rss_url, num):
    """
    获取一个 RSS 源的最新 n 篇文章的 title n 篇文章的发布时间并且返回。
    """
    try:
        articles = []
        d = feedparser.parse(rss_url)
        if not hasattr(d, 'entries'):
            logging.warning(f"No entries found in feed: {rss_url}")
            return []
        for entry in d.entries[:int(num)]:
            title = entry.get('title', '')
            pub_date = entry.get('published', '') or entry.get('updated', '')
            articles.append({"title": title, "pub_date": dt_to_str(str_to_dt(pub_date))})
        return articles
    except Exception as e:
        logging.error(f"Failed to parse feed {rss_url}: {e}")
        return []




rss_list = [
    # ('News','FT - World', 'https://www.ft.com/world?format=rss'),
    # ('News','FT - US', 'https://www.ft.com/us?format=rss'),
    # ('News','FT - Companies', 'https://www.ft.com/companies?format=rss'),
    # ('News','FT - Tech', 'https://www.ft.com/technology?format=rss'),
    # ('News','FT - Markets', 'https://www.ft.com/markets?format=rss'),
    # ('News','FT - Opinion', 'https://www.ft.com/opinion?format=rss'),
    # ('News','FT - Life & Arts', 'https://www.ft.com/life-arts?format=rss'),
    #     ('News','Nature - Latest Research','https://rsshub.app/nature/research/nature'),
    #     ('News','Nature - Biotechnology','https://rsshub.app/nature/research/nbt'),
    # ('News','Nature - Neuroscience','https://rsshub.app/nature/research/neuro'),
    # ('News','Nature - Genetics','https://rsshub.app/nature/research/ng'),
    # ('News','Nature - Immunology','https://rsshub.app/nature/research/ni'),
    # ('News','Nature - Method','https://rsshub.app/nature/research/nmeth'),
    # ('News','Nature - Chemistry','https://rsshub.app/nature/research/nchem'),
    # ('News','Nature - Materials','https://rsshub.app/nature/research/nmat'),
    # ('News','Nature - Machine Intelligence','https://rsshub.app/nature/research/natmachintell'),
    # ('News', 'WSJ 中国 - 中文', 'https://rsshub.app/wsj/zh-cn/china'),
    # ('News', 'WSJ 金融市场 - 中文', 'https://rsshub.app/wsj/zh-cn/markets'),
    # ('News', 'WSJ 经济 - 中文', 'https://rsshub.app/wsj/zh-cn/economy'),
    # ('News', 'WSJ 商业 - 中文', 'https://rsshub.app/wsj/zh-cn/business'),
    # ('News', 'WSJ 科技 - 中文', 'https://rsshub.app/wsj/zh-cn/technology'),
    # ('News', 'WSJ 专栏与观点 - 中文', 'https://rsshub.app/wsj/zh-cn/opinion'),
    ('News', 'The Guardian - Editorial', 'https://rsshub.app/guardian/editorial')

]

if __name__ == "__main__":
    # print(int(-8))
    print(new_passwd())
    print(get_rss_latest_titles('https://rsshub.app/economist/global-business-review/cn-en', 1))
    # d = feedparser.parse("https://feedx.net/rss/economistp.xml")

    # print(d.entries[0])
    # a = {'name': 'tom', 'age': 22}
    # if 'hahah' in a:
    #     print("ok")
    # for rss in rss_list:
    #     path = '/api/v2/rss/manager'
    #     data = {'key': config.RSS2EBOOK_KEY,
    #             'user_name': 'admin',
    #             'creator': 'admin',
    #             "title": rss[1],
    #             "url": rss[2],
    #             "is_fulltext": "Flase",
    #             "category": rss[0],
    #             "librss_id": 1
    #             }

        # print(data)
        #     # request_url = "http://127.0.0.1:8080"
        # res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS, timeout=60)
        # print(rss)
        # print(res.text, res.status_code)
