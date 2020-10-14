"""Выгрузка новостей с сайта https://mkommunar.ru"""

import re
import requests


def mk_news_finder(url):
    """Создаёт массив с информацией о каждой новости"""

    list_of_news_info = []
    # Проходим по всем страницам с новостями на сайте
    for page in range(56): 

        res = requests.get(url + "page/" + str(page) + "/")
        # Ищем кусок htlm-кода с перечислением новостей и ссылками на них
        news = re.findall(r'<ul id="infinite-articles" class="modern-list js-masonry">.+?<div class="defaultpag">', \
                res.text, re.S)
        # Выделяем каждый сегмент с новостью отдельно
        for segment in news:
            page_news_info = re.findall(r'<div class="modern-list-content.*?</ul>', segment, re.S)
            list_of_news_info.extend(page_news_info)
     # В итоговом массиве каждый элемент - информация о конретной новости
    return list_of_news_info


def data_extractor(html_info_list):
    """Извлекает и записывает в файл .txt в требуемом формате 
        ссылки на новости, их тексты и заголовки, информацию о времени 
        загрузки новостей
    """

    for news_info in html_info_list:

        url = re.findall(r'<h2><a href="(.*?)">', news_info)[0]
        title = re.findall(r'<a href=".*?">(.*?)<\/a><\/h2>', news_info)[0]
        author = re.findall(r'rel="author">(.*?)<\/a>', news_info)[0]
        # Здесь и далее if-else решают проблему отличий формата старых и новых страниц
        if len(re.findall(r'<span>(.*?)</span> назад', news_info)) == 0:
            years = re.findall(r'<li class="time-article updated">(.*?)<\/li>', news_info)[0]
        else:
            years = re.findall(r'<span>(.*?)<\/span> назад', news_info)[0]
        date = years + "назад"

        text_url = requests.get(url)

        if len(re.findall(r'<p style="text-align: justify;">(.*?)<\/p>', text_url.text)) != 0:
            news = re.findall(r'<p style="text-align: justify;">(.*?)<\/p>', text_url.text)
        else:
            news = re.findall(r'<p>(.+?)<\/p>', text_url.text, re.S)[:-2]
        
        with open("news.txt", "a", encoding="utf-8") as f:
            f.write("=====" + "\n")
            f.write(url + "\n" + "https://mkommunar.ru" + "\n" + date + "\n" + 
                author + "\n" + title + "\n" + "".join(news) + "\n")
            



def main():
    url = "https://mkommunar.ru/category/news-voronezh/"
    news_html_info = mk_news_finder(url)
    data_extractor(news_html_info)


if __name__ == "__main__":
    main()