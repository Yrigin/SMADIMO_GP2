import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logging import logger
from src.utils.file_utils import generate_csv_filename

# Настройка удаленного WebDriver для подключения к Selenium 
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

logger.info(f"Init webdriver")
driver = webdriver.Remote(
    command_executor='http://109.73.196.223:4444/wd/hub',
    options=options
)

logger.info(f"Get first page")
# Переход на страницу с квартирами
driver.get("https://donstroy.moscow/full-search/")

# Ожидание загрузки страницы
time.sleep(7)

# Закрываем баннеры
logger.info(f"close banners")
driver.find_element(By.ID, "jivo_close_button").click()
driver.find_element(By.CLASS_NAME, "d-cookie__button").click()

# Генерация имени файла для сохранения данных
filename = generate_csv_filename("donstroi")
logger.info(f"Saving data to {filename}")

# Открытие CSV файла для записи данных
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Price", "Square", "Address"])

    current_page = 1
    while current_page < 40:
        logger.info(f"Fetching data for page {current_page}")

        # Сбор информации о квартирах на текущей странице
        flats = driver.find_elements(By.CLASS_NAME, "d-flat-card")
        for flat in flats:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", flat) # листаем до лота
                title = flat.find_element(By.CLASS_NAME, "d-flat-card__title").text
                price = flat.find_element(By.CLASS_NAME, "d-flat-card__price").text
                square = flat.find_element(By.CLASS_NAME, "d-flat-card__square").text
                address = flat.find_element(By.CLASS_NAME, "d-flat-card__position").text

                if "\n" in price:
                    price = price.split("\n")[1]
                if "\n" in address:
                    address = address.split("\n")[0]
                
                print([title, price, square, address])
                if len(title) > 0:
                    writer.writerow([title, price, square, address])
            except NoSuchElementException:
                logger.warning("Element not found, skipping...")
                continue

        logger.info(f"Fetched {len(flats)} flats from page {current_page}")

        # Проверка наличия следующей страницы
        try:
            buttons = driver.find_elements(By.CLASS_NAME, "d-press-pager__pagination-bullet")
            next_button = None
            for button in buttons:
                if button.get_attribute("data-page-index") == str(current_page + 1):
                    next_button = button
                    break

            if next_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button))
                next_button.click()
                current_page += 1
                time.sleep(10)
            else:
                break
        except NoSuchElementException:
            break

# Закрытие браузера
driver.quit()

logger.info(f"Data successfully saved to {filename}")
