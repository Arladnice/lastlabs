import requests
from pprint import pprint as pp
from bs4 import BeautifulSoup
from sqlalchemy import Column, String, Integer, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import News, session
from bottle import redirect, request, route, run, template
s = session()


def save_database(dicts):
    s = session()
    rows = s.query(News).filter().all()
    bd_labels = []
    for row in rows:
        bd_labels.append(row.title)
    #print(bd_labels)
    for current_new in dicts:
        if current_new['title'] not in bd_labels:
            news = News(title=current_new['title'],
                        author=current_new['author'],
                        url=current_new['url'],
                        comments=current_new['comments'])
            s.add(news)
    s.commit()


def extract_news(page):
    main = page.find_all('article', {'class': 'post'})[1:]
    news_list = []
    print('main:', main)
    for elem in main:
        author = elem.find_next('span', {'class': 'autor'})
        title = elem.find_next('span', {'itemprop': 'name'})
        comments = elem.find_next('a', {'class': 'v-count'})
        url = elem.find_next('a', {'rel': 'bookmark'})

        try:
            news_list.append({
                'author': author.text,
                'title': title.text,
                'comments': comments.text,
                'url': url['href']
            })
        except:
            pass

    return news_list


def get_news(url, n_pages):
    """ Collect news from a given web page """
    lst = []
    for i in range(n_pages):
        url = "https://4pda.ru/page/" + str(i + 1)
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        lst.extend(news_list)
    return lst


def split_row(string):
    word = ''
    word_list = []
    for i in range(len(string)):
        if string[i] != ' ':
            word += string[i]
        else:
            word_list.append(word)
            word = ''
    word_list.append(word)
    return word_list