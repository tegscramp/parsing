import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import csv
import datetime

URL = 'https://auto.ria.com/uk/newauto/' # Вставить ссылку для парсига
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0','accept':'*/*'}
HOST = 'https://auto.ria.com'
DATE = datetime.datetime.now()

def get_html(url, params=None):  # params - передаем номера страницы ...marka-skoda/?page=7
    req = requests.get(url, headers=HEADERS, params=params)
    return req

# Получаем количество страниц
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1

# В этой функции формируем массив с данными из карточки товара
def get_categories(html):
    soup = BeautifulSoup(html, 'html.parser') # В аргументе передеаем тип документа с которым мы работаем.
    list_categories = soup.find_all('a', class_='item-brands') # Получаем коллекцию карточек товаров
    list = []
    for item in list_categories:
        list.append({
            'title': item.find('span').find('span').get_text(strip=True),
            'url': HOST + item.get('href')
        })
    return list

# В этой функции формируем массив с данными из карточки товара
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser') # В аргументе передеаем тип документа с которым мы работаем.
    items = soup.find_all('div', class_='proposition') # Получаем коллекцию карточек товаров
    cars = []
    for item in items:
        uah_price = item.find('div', class_='proposition_price').find('span', class_="size13"), # Проверяем есть ли цена в UAH
        if uah_price:
            uah_price = item.find('div', class_='proposition_price').find_all('span')[-1].get_text(strip=True).split('грн')[0].replace(' ', '')
        else:
            uah_price = ''

        price_old = item.find('div', class_='proposition_price_old') # Проверяем есть ли цена в UAH
        if price_old:
            price_old = item.find('div', class_='proposition_price_old').find('span', class_="red").get_text(strip=True).split('$')[0]
        else:
            price_old = ''

        volume = item.find('div', class_='proposition_information').find('span').find_all('span')
        if len(volume) > 1: # Сделать проврку на количество спанов
            volume = item.find('div', class_='proposition_information').find('span').find_all('span')[1].get_text(strip=True) # Получаем объем двигателя
        else:
            volume = 'Не указан'
        cars.append({
            'title': item.find('h3', class_='proposition_name').find('strong', class_='link').get_text(strip=True), # Получаем заголовки карточки. strip=True - Удаляем лишние пробелы в начале и конце текста
            'region': item.find('div', class_='proposition_region').find('strong').get_text(strip=True),
            'company': item.find('div', class_='proposition_region').get_text(strip=True).replace(item.find('div', class_='proposition_region').find('strong').get_text(strip=True), '').replace('•', ''), # Получаем название продавца // Через replace удалем название города и точку
            'price_old': price_old,
            'price_usd': item.find('div', class_='proposition_price').find('span', class_='green').get_text(strip=True).split('$')[0].replace(' ', ''), # Получаем цену в $
            'price_uah': uah_price,
            'link': HOST + item.find('a', class_='proposition_link').get('href'), # Получаем ссылку через метод .get('href')
            'meta': item.find('div', class_='proposition_equip').find('span', class_='link').get_text(strip=True), # Получаем ттх авто
            'fuel': item.find('div', class_='proposition_information').find('span').find('span').get_text(strip=True), # Получаем тип топлива
            'volume': volume,
            'transmission': item.find('div', class_='proposition_information').find_all('span')[4].get_text(strip=True), # Коробка
            'drive' : item.find('div', class_='proposition_information').find_all('span')[-1].get_text(strip=True), # Привод
            'photo': item.find('div', class_='proposition_photo').find('img').get('src')
        })
    return cars

# Рабоем с csv файлом
def safe_file(items, path):
    with open(path, 'w', newline='') as file: # Открываем файл для записи
        writer = csv.writer(file, delimiter=';') # Указываем чтоб разделялись значения точкой с зяпятой тогда откроется в exel
        writer.writerow(['Марка', 'Город', 'Продавец', 'Старая цена в $', 'Цена в $', 'Цена в UAH', 'ссылка', 'Ттх', 'Топливо', 'Объем', 'Трансмиссия', 'Привод', 'Фото'])
        for item in items:
            writer.writerow([item['title'], item['region'], item['company'], item['price_old'], item['price_usd'], item['price_uah'], item['link'], item['meta'], item['fuel'], item['volume'], item['transmission'], item['drive'], item['photo']])

# Функция парсига
def parse():
    html = get_html(URL)
    if html.status_code == 200:
        catigories = get_categories(html.text)
        print('Начало парсинга auto.ria.com -> New Auto')
        print('https://auto.ria.com/uk/newauto/')
        for item in catigories:
            html_cur = get_html(item['url'])
            FILE = item['title'] + '_' + str(DATE.date()) + '.csv'
            title = item['title']
            pages_count = get_pages_count(html_cur.text)
            cars = []
            for page in range(1, pages_count + 1):  # Метод range() генерирует список от заданного количество элементов до конечного количества элементов, конечный элемент не учвствует в итерации
                print(f'Авто {title}. Парсинг страницы {page} из {pages_count}...')
                html = get_html(item['url'], params={'page': page})
                cars.extend(get_content(html_cur.text))  # Расширяем новый массив
            safe_file(cars, FILE)
            print(f'Авто {title}: получено {len(cars)} автомобилей')
    else:
        print('Error')

parse()