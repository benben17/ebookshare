import logging

import feedparser

import config
from book.utils.date_util import dt_to_str, str_to_dt


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
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:04:19",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5100832596951040,
      "subscribed": 0,
      "title": "The Economist / Books and arts",
      "url": "https://rsshub.app/economist/books-and-arts"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:25",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5110721893367808,
      "subscribed": 2,
      "title": "The Economist / The world this week",
      "url": "https://rsshub.app/economist/the-world-this-week"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:24",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5114949751799808,
      "subscribed": 3,
      "title": "The Economist / China",
      "url": "https://rsshub.app/economist/china"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-21 15:05:00",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5632192797474816,
      "subscribed": 2,
      "title": "The Economist / Business-review 商论中-英文",
      "url": "https://rsshub.app/economist/global-business-review/cn-en"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:43:46",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5632675578642432,
      "subscribed": 1,
      "title": "The Economist / International",
      "url": "https://rsshub.app/economist/international"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:04:19",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5645343853117440,
      "subscribed": 2,
      "title": "The Economist / Graphic detail",
      "url": "https://rsshub.app/economist/graphic-detail"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:24",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5646113927331840,
      "subscribed": 2,
      "title": "The Economist / Leaders",
      "url": "https://rsshub.app/economist/leaders"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:04:16",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5667323952234496,
      "subscribed": 0,
      "title": "The Economist / The Americas",
      "url": "https://rsshub.app/economist/the-americas"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:17",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5673671846789120,
      "subscribed": 1,
      "title": "The Economist / Finance and Economics",
      "url": "https://rsshub.app/economist/finance-and-economics"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:17",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5687892684832768,
      "subscribed": 1,
      "title": "The Economist / Europe",
      "url": "https://rsshub.app/economist/europe"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:43:45",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5714113258848256,
      "subscribed": 0,
      "title": "The Economist / Middle East and Africa",
      "url": "https://rsshub.app/economist/middle-east-and-africa"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:43:48",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5721633947910144,
      "subscribed": 0,
      "title": "The Economist / Special reports",
      "url": "https://rsshub.app/economist/special-report"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:22",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5726049644052480,
      "subscribed": 0,
      "title": "The Economist / Science and technology",
      "url": "https://rsshub.app/economist/science-and-technology"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:44:20",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5744557597655040,
      "subscribed": 1,
      "title": "The Economist / Business",
      "url": "https://rsshub.app/economist/business"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:04:18",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5752835274702848,
      "subscribed": 1,
      "title": "The Economist / Asia",
      "url": "https://rsshub.app/economist/asia"
    },
    {
      "category": "Economist",
      "created_time": "2023-04-11 07:04:17",
      "is_fulltext": True,
      "is_subscribe": True,
      "librss_id": 5766792777564160,
      "subscribed": 0,
      "title": "The Economist / United States",
      "url": "https://rsshub.app/economist/united-states"
    }
  ]

if __name__ == "__main__":
    # print(int(-8))
    # print(new_passwd())
    # print(get_rss_latest_titles('https://rsshub.app/economist/global-business-review/cn-en', 1))
    # # d = feedparser.parse("https://feedx.net/rss/economistp.xml")

    # print(d.entries[0])
    # a = {'name': 'tom', 'age': 22}
    # if 'hahah' in a:
    #     print("ok")
    for rss in rss_list:
        path = '/api/v2/rss/manager'
        data = {'key': config.RSS2EBOOK_KEY,
                'user_name': 'admin',
                'creator': 'admin',
                "title": rss['title'],
                "url": rss['url'],
                "is_fulltext": True,
                "category": rss['category'],
                "librss_id": rss['librss_id']
                }

        # print(data)
        #     # request_url = "http://127.0.0.1:8080"
        # res = requests.post(get_rss_host() + path, data=data, headers=config.HEADERS, timeout=60)
        # # print(rss)
        # print(res.text, res.status_code)
