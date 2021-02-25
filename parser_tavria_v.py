import requests
from bs4 import BeautifulSoup
import csv
import datetime
import zipfile
import os

URL = 'https://www.tavriav.ua/catalog/discount/' # Вставить ссылку для парсига
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0','accept':'*/*'}
HOST = 'https://www.tavriav.ua'
DATE = datetime.datetime.now()
FILE = 'tavria_v_' + str(DATE.date()) + '.csv'
ARC_NAME = FILE.replace('.csv', '.zip')
PATH = os.getcwd() + '\\'

def get_html(url, params=None):  # params - передаем номера страницы ...marka-skoda/?page=7
    req = requests.get(url, headers=HEADERS, params=params)
    return req

# Получаем количество страниц
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('ul', class_='pagination').find_all('li')
    if pagination:
        return int(pagination[-2].find('a').get_text(strip=True).replace('...', ''))
    else:
        return 1

# В этой функции формируем массив с данными из карточки товара
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser') # В аргументе передеаем тип документа с которым мы работаем.
    items = soup.find('div', class_='catalog-products__container').find_all('div', class_='products__item') # Получаем коллекцию карточек товаров
    array = []
    for item in items:
        array.append({
            'title': item.find('p', class_='product__title').get_text(strip=True), # Получаем заголовки карточки. strip=True - Удаляем лишние пробелы в начале и конце текста
            'image': item.find('div', class_='product__image').find('img').get('src'),
            'link': HOST + item.find('p', class_='product__title').find('a').get('href'),
            'discount': item.find('span', class_='discount__value').get_text(strip=True).replace('.', ','),
            'new_price': item.find('span', class_='price__discount').get_text(strip=True).replace(' ₴', '').replace('.', ','),
            'old_price': item.find('span', class_='price__old').get_text(strip=True).replace(' ₴', '').replace('.', ',')
        })
    return array

# Рабоем с csv файлом
def safe_file(items, path):
    with open(path, 'w', newline='') as file: # Открываем файл для записи
        writer = csv.writer(file, delimiter=';') # Указываем чтоб разделялись значения точкой с зяпятой тогда откроется в exel
        writer.writerow(['Название', 'Фото', 'Ссылка', 'Скидка %', 'Акционная цена грн.', 'Обычная цена грн.'])
        for item in items:
            writer.writerow([item['title'], item['image'], item['link'], item['discount'], item['new_price'], item['old_price']])

# Парсим данные
def parse():
    html = get_html(URL)
    if html.status_code == 200:
        print('Парсинг товаров со скидкой на сайте tavriav.ua')
        print('https://www.tavriav.ua/catalog/discount/')
        array = []
        pages_count = get_pages_count(html.text) # Находим количество разделов как правило в низу сайта
        for page in range(1, pages_count + 1): # Метод range() генерирует список от заданного количество элементов до конечного количества элементов, конечный элемент не учвствует в итерации
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            array.extend(get_content(html.text)) # Расширяем новый массив
        safe_file(array, FILE)
        zip_files()
    else:
        print('Error')

# Архивируем данные
def zip_files():
    # Создаем архив
    print('Creating zip file...')
    arc = zipfile.ZipFile(PATH + ARC_NAME, 'w')
    arc.write(FILE, compress_type=zipfile.ZIP_DEFLATED)
    arc.close()

    # Удаляем csv файл
    print('Deleting csv file...')
    os.remove(PATH + FILE)

parse()
