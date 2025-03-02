import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
        logging.FileHandler("ingrad_scraping.log", encoding="utf-8"),  # Логи в файл с кодировкой UTF-8
        logging.StreamHandler()]
)

# Настройка опций для Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки SSL

try:
    # Автоматическая установка ChromeDriver
    logging.info("Установка ChromeDriver")
    service = Service(ChromeDriverManager().install())

    # Инициализация драйвера
    logging.info("Инициализация веб-драйвера")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Создание DataFrame для хранения данны
    data = []

    # Перебор страниц с 1 по 5
    for page in range(1, 288):
        url = f"https://www.ingrad.ru/search/flats?page={page}"
        logging.info(f"Переход на страницу: {url}")
        driver.get(url)
        time.sleep(5)  # Ожидание загрузки страницы

        # Поиск всех строк с классом "table-row"
        rows = driver.find_elements(By.CSS_SELECTOR, 'tr.table-row')
        logging.info(f"Найдено строк: {len(rows)}")

        # Обработка каждой строки
        for row in rows:
            # Поиск всех ячеек с классом "table-cell table-row__cell table-cell_pointer"
            cells = row.find_elements(By.CSS_SELECTOR, 'td.table-cell.table-row__cell.table-cell_pointer')
            
            # Извлечение текста из ячеек
            row_data = [cell.text.strip() for cell in cells]
            
            # Добавление данных в список
            data.append(row_data)
            # logging.info(f"Добавлены данные: {row_data}")

    # Закрытие драйвера
    logging.info("Закрытие веб-драйвера")
    driver.quit()

    # Создание DataFrame
    df = pd.DataFrame(data)

    # Сохранение данных в Excel
    output_file = "ingrad_flats.xlsx"
    df.to_excel(output_file)
    logging.info(f"Данные успешно сохранены в файл {output_file}.")

except Exception as e:
    logging.error(f"Произошла ошибка: {e}")
