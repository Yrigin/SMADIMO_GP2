import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import sys

# Добавляем путь к корневой папке проекта, чтобы импортировать модули из других папок
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.file_utils import generate_csv_filename
from src.utils.logging import logger


# Настройка опций для Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки SSL

try:
    # Автоматическая установка ChromeDriver
    logger.info("Установка ChromeDriver")
    service = Service(ChromeDriverManager().install())

    # Инициализация драйвера
    logger.info("Инициализация веб-драйвера")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Переход на главную страницу
    main_url = "https://www.ingrad.ru/#projects"
    logger.info(f"Переход на главную страницу: {main_url}")
    driver.get(main_url)
    time.sleep(5)  # Ожидание загрузки страницы

    # Сбор всех ссылок на проекты
    project_links = []
    projects = driver.find_elements(By.CSS_SELECTOR, 'li.big-project-card a.big-project-card__max-link')
    for project in projects:
        link = project.get_attribute("href")
        project_links.append(link)

    logger.info(f"Найдено {len(project_links)} проектов.")

    # Сбор данных с каждой страницы проекта
    project_data = []

    for link in project_links:
        logger.info(f"Переход на страницу проекта: {link}")
        driver.get(link)
        time.sleep(3)  # Ожидание загрузки страницы

        # Поиск заголовка h1 с классом "hero-image__title"
        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.hero-image__title').text
            logger.info(f"Заголовок найден: {title}")
        except Exception as e:
            title = "Заголовок не найден"
            logger.error(f"Ошибка при поиске заголовка: {e}")

        # Поиск текста в объекте div с классом "tabs-text__description"
        try:
            description = driver.find_element(By.CSS_SELECTOR, 'div.tabs-text__description').text
            logger.info(f"Описание найдено: {description[:50]}...")  # Логируем первые 50 символов описания
        except Exception as e:
            description = "Описание не найдено"
            logger.error(f"Ошибка при поиске описания: {e}")

        # Сохранение данных
        project_data.append({
            "Ссылка": link,
            "Заголовок": title,
            "Описание": description
        })

    # Закрытие драйвера
    logger.info("Закрытие веб-драйвера")
    driver.quit()

    # Сохранение данных в CSV
    df = pd.DataFrame(project_data)
    output_file = "ingrad_description-02-03-2025.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"Данные сохранены в файл {output_file}")

except Exception as e:
    logger.critical(f"Критическая ошибка: {e}")
