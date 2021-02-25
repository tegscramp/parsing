import requests
from bs4 import BeautifulSoup
import csv
import datetime

URL = 'https://fozzyshop.ua/ru/prices-drop' # Вставить ссылку для парсига
# URL = 'https://fozzyshop.ua/ru/s-15/prices-drop/kategoriya-avtomaticheskie'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0','accept':'*/*'}
HOST = 'https://auto.ria.com'
DATE = datetime.datetime.now()
FILE = 'fozzyshop.csv'

def get_html(url, params=None):  # params - передаем номера страницы ...marka-skoda/?page=7
    req = requests.get(url, headers=HEADERS, params=params)
    return req

# Получаем количество страниц
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('ul', class_='page-list')
    if pagination:
        return int(soup.find('ul', class_='page-list').find_all('li')[-2].find('a').get_text(strip=True))
    else:
        return 1

# В этой функции формируем массив с данными из карточки товара
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser') # В аргументе передеаем тип документа с которым мы работаем.
    items = soup.find_all('div', class_='js-product-miniature-wrapper') # Получаем коллекцию карточек товаров
    array = []
    for item in items:
        array.append({
            'title': item.find('div', class_='product-title').find('a').get_text(strip=True), # Получаем заголовки карточки. strip=True - Удаляем лишние пробелы в начале и конце текста
            'link': item.find('div', class_='product-title').find('a').get('href'),
            'packing': item.find('div', class_='product-description').find_all('div')[3].find('a').get_text(strip=True).replace('Фасовка: ', ''),
            'articulation': item.find('div', class_='product-description').find_all('div')[4].find('a').get_text(strip=True).replace('Артикул: ', ''),
            'current_price': item.find('span', class_='product-price').get('content'),
            'regular_price': item.find('span', class_='regular-price').get_text(strip=True).replace('\xa0грн', ''),
            'last_day': item.find('div', class_='count-down-timer').get('data-countdown-product'),
            'discount': item.find('span', class_='flag-discount-value').get_text(strip=True).replace('\xa0грн', ''),
            'photo': item.find('div', class_='thumbnail-container').find('img').get('src')
        })
    return array

# Рабоем с csv файлом
def safe_file(items, path):
    with open(path, 'w', newline='') as file: # Открываем файл для записи
        writer = csv.writer(file, delimiter=';') # Указываем чтоб разделялись значения точкой с зяпятой тогда откроется в exel
        writer.writerow(['Название', 'Фото', 'Ссылка', 'Фасовка', 'Артикул', 'Скидка %', 'Акционная цена грн.', 'Обычная цена грн.', 'Последний день акции'])
        for item in items:
            writer.writerow([item['title'], item['photo'], item['link'], item['packing'], item['articulation'], item['discount'], item['current_price'], item['regular_price'], item['last_day']])

# Парсим данные
def parse():
    html = get_html(URL)
    if html.status_code == 200:
        print('Парсинг товаров со скидкой на сайте fozzyshop.ua')
        print('https://fozzyshop.ua/ru/prices-drop')
        array = []
        pages_count = get_pages_count(html.text) # Находим количество разделов как правило в низу сайта
        for page in range(1, pages_count + 1): # Метод range() генерирует список от заданного количество элементов до конечного количества элементов, конечный элемент не учвствует в итерации
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            array.extend(get_content(html.text)) # Расширяем новый массив
        safe_file(array, FILE)
        # print(f'Получено {len(array)} автомобилей')
    else:
        print('Error')

parse()
