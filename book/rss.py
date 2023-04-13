import feedparser


def is_rss_feed(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        if feed.get('version'):
            return True
    except:
        pass
    return False


def get_rss_latest_titles(rss_url):
    """
    获取一个 RSS 源的最新 10 篇文章的 title。
    """
    d = feedparser.parse(rss_url)
    print(d.get('version'))
    titles = []
    for entry in d.entries[:10]:
        # print(entry.description)
        titles.append(entry.title)
    return titles


rss_list = [
    ('News','FT - World', 'https://www.ft.com/world?format=rss'),
    ('News','FT - US', 'https://www.ft.com/us?format=rss'),
    ('News','FT - Companies', 'https://www.ft.com/companies?format=rss'),
    ('News','FT - Tech', 'https://www.ft.com/technology?format=rss'),
    ('News','FT - Markets', 'https://www.ft.com/markets?format=rss'),
    ('News','FT - Opinion', 'https://www.ft.com/opinion?format=rss'),
    ('News','FT - Life & Arts', 'https://www.ft.com/life-arts?format=rss'),
]



if __name__ == "__main__":
    print("aa")