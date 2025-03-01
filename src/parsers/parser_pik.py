import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import sys

# Добавляем путь к корневой папке проекта, чтобы импортировать модули из других папок
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.file_utils import generate_csv_filename
from src.utils.logging import logger
# Настройка логирования

filename = generate_csv_filename("pik")
# Список для хранения данных объявлений
ads_data = []

# Функция для получения HTML-кода страницы
def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        logger.info(f"Запрос страницы: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        logger.info("Страница успешно загружена.")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе страницы {url}: {e}")
        return None

# Функция для парсинга данных с одной страницы
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='sc-llwFvi jCWTdi')

    if not items:
        logger.warning("На странице не найдено объявлений.")
        return

    logger.info(f"Найдено {len(items)} объявлений на странице.")

    for item in items:
        try:
            # Парсинг названия
            title = item.find('span', class_='styles__RoomsArea-j8px38-6 kJHeeR')
            title_text = title.text.strip() if title else "Нет названия"
            logger.debug(f"Название: {title_text}")

            # Парсинг цены
            price = item.find("span", class_="styles__MainPriceText-j8px38-9 dmzhmf")
            price_text = price.text.strip() if price else "Нет цены"
            logger.debug(f"Цена: {price_text}")

            # Парсинг ссылки на объявление
            link = item.find("a", class_="styles__FlatCardDefault-j8px38-0 cmoPeS")
            link_url = "https://www.pik.ru" + link["href"] if link else "Нет ссылки"
            logger.debug(f"Ссылка: {link_url}")

            # Парсинг метро
            address_block = item.find("div", class_="styles__FlatCardSubTitle-sc-14xw5ot-0 eZXPkj FlatCardSubTitle")
            address_text = address_block.get_text(strip=True) if address_block else "Нет информации о метро и адресе"
            logger.debug(f"Метро: {address_text}")

            # Парсинг корпуса/этажа
            floor = item.find("div", class_="styles__BulkFloor-j8px38-4 gnxucF")
            floor_text = floor.find('span', class_="styles__BulkFloorText-j8px38-5 kcVNPb") if floor else None
            floor_text_text = floor_text.text.strip() if floor_text else "Нет информации"
            logger.debug(f"Корпус/Этаж: {floor_text_text}")

            # Парсинг заселения
            move_in = item.find("div", class_="styles__Settlement-j8px38-15 OTGjy")
            move_in_text = move_in.get_text(strip=True) if move_in else "Нет информации"
            logger.debug(f"Заселение: {move_in_text}")

            # Создаем словарь с данными объявления
            ad_info = {
                "Ссылка на объявление": link_url,
                "Название": title_text,
                "Цена": price_text,
                "Метро": address_text,
                "Корпус/Этаж": floor_text_text,
                "Заселение": move_in_text
            }

            # Добавляем словарь в список
            ads_data.append(ad_info)
            # logger.info(f"Добавлено объявление: {title_text}")

        except Exception as e:
            logger.error(f"Ошибка при парсинге объявления: {e}")

# Основная функция для парсинга всех страниц
def main():
    base_url = 'https://www.pik.ru/search'
    total_pages = 2

    for page in range(1, total_pages + 1):
        url = f"{base_url}?flatPage={page}"
        logger.info(f"Парсинг страницы {page}/{total_pages}: {url}")
        html = get_page(url)
        if html:
            parse_page(html)

        # Задержка между запросами
        time.sleep(2)

    # Сохраняем данные в DataFrame
    global df_pik
    df_pik = pd.DataFrame(ads_data)
    logger.info("Данные успешно сохранены в DataFrame.")

    # Сохраняем DataFrame в CSV (опционально)
    try:
        df_pik.to_csv(filename, index=False, encoding='utf-8')
        logger.info("Данные успешно сохранены в файл pik_data.csv.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в CSV: {e}")

# Вызов основной функции
if __name__ == "__main__":
    main()


