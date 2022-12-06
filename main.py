import requests
import bs4
import time
import warnings
import pprint
import logging
import re
from fake_headers import Headers
warnings.filterwarnings('ignore')

KEYWORDS = ['дизайн', 'фото', 'web', 'Python','поехали']
pattern = '[\f\n\r\t\v!?,.«»—*\"\':;()]'

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

url = 'https://habr.com'
get_url = f'{url}/ru/all'
head = Headers(os="mac", headers=True).generate()

def get_article(session, url, headers):
    """Функция для получения данных с сайта"""
    response = session.get(url, headers=headers, verify=False)
    logger.info(f' get_article {response}')
    text = response.text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    articles = soup.find_all('article')
    return articles


def read_article(articles, keywords, pattern):
    """Функция для преобразования полученных данных 
    с сайта и приведение их к необходимой структуре"""
    result = []
    for article in articles:
        dates = article.find_all(class_ = 'tm-article-snippet__datetime-published')
        date = [data.time['title'].split(',')[0]  for data in dates]
        time = [data.time['title'].split(',')[1].replace(' ', '')  for data in dates]
        href = article.find('h2').find('a')['href']
        full_href = f'{url}{href}'
        title = article.find('h2').find('span').text
        split_title = set([re.sub(pattern, '', x.lower()) for x in title.split(' ')])
        snippet = article.find_all(class_ = 'tm-article-body tm-article-snippet__lead')
        body_v1 = snippet[0].find_all(class_ = 'article-formatted-body article-formatted-body article-formatted-body_version-1')
        body_v2 = snippet[0].find_all(class_ = 'article-formatted-body article-formatted-body article-formatted-body_version-2')
        if body_v1:
            body = body_v1
        elif body_v2:
            body = body_v2
        split_body = set([re.sub(pattern, '', x.lower()) for x in body[0].text.split(' ')])
        if len((split_title | split_body) & set([x.lower() for x in keywords])):
            result.append(f'{date[0]} в {time[0]} - {title} ===> {full_href}')
    return result


def next_url(session, url, headers):
    """Функция для получения адреса следующей сраницы"""
    response = session.get(url, headers=headers, verify=False)
    logger.info(f' next_url {response}')
    text = response.text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    pagination = soup.find_all(class_ = 'tm-pagination')
    pagination_page = pagination[0].find(id = 'pagination-next-page')['href']
    return pagination_page


def load_article(count, get_url, head, KEYWORDS):
    with requests.Session() as sess:
        for i in range(count):
            time.sleep(3)
            print(f'URL:    {get_url}')
            art = get_article(sess, get_url, head)
            result = read_article(art, KEYWORDS, pattern)
            get_url = f'{url}{next_url(sess, get_url, head)}'
            pprint.pprint(result)


if __name__ == '__main__':
    load_article(int(input('Введи кол-во просматриваемых страниц: ')), get_url, head, KEYWORDS)