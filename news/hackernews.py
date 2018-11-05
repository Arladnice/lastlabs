from bottle import (
    route, run, template, request, redirect
)

from scraputils import get_news, split_row, save_database
from db import News, session
from bayes import NaiveBayesClassifier
s = session()
classifier = NaiveBayesClassifier()
mark_news = s.query(News).filter(News.label != None).all()
x_title = [row.title for row in mark_news]
y_lable = [row.label for row in mark_news]
classifier.fit(x_title, y_lable)
print(classifier.fit(x_title, y_lable))

@route('/')
@route('/news')
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label")
def add_label():
    label = request.query.label
    id = request.query.id
    s = session()
    items = s.query(News).filter(News.id == id).update({"label": label})
    s.commit()
    redirect('/news')
    

@route('/update_news')
def update_news():
    dicts = get_news('http://4pda.ru', 3)
    save_database(dicts)
    redirect('/news')
    
    
@route('/classify')
def classify_news():
    s = session()
    recently_mark_news = s.query(News).filter(News.title not in x_title and News.label != None).all()
    title_extra = [row.title for row in recently_mark_news]
    label_extra = [row.label for row in recently_mark_news]
    classifier.fit(title_extra, label_extra)
    not_mark_news = s.query(News).filter(News.label == None).all()
    x = [row.title for row in not_mark_news]
    labels = classifier.predict(x)
    for i in range(len(not_mark_news)):
        not_mark_news[i].label = labels[i]
    classified_news = [not_mark_news[i] for i in range(len(not_mark_news))]
    return template('news_template', rows=classified_news)


if __name__ == "__main__":
    run(host="localhost", port=8080)
