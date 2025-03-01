from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.FileHandler("a101_parsing.log", encoding="utf-8"),  # Логи в файл с кодировкой UTF-8
        logging.StreamHandler()  # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)

# Настройка опций для Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки SSL

# Автоматическая установка ChromeDriver
try:
    logger.info("Установка ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    logger.info("ChromeDriver успешно установлен.")
except Exception as e:
    logger.error(f"Ошибка при установке ChromeDriver: {e}")
    raise

# Инициализация драйвера
try:
    logger.info("Инициализация драйвера...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger.info("Драйвер успешно инициализирован.")
except Exception as e:
    logger.error(f"Ошибка при инициализации драйвера: {e}")
    raise

# Переход на страницу со списком проектов
try:
    logger.info("Переход на страницу со списком проектов...")
    driver.get("https://a101.ru/projects/?view=list")
    time.sleep(5)  # Ожидание загрузки страницы
    logger.info("Страница успешно загружена.")
except Exception as e:
    logger.error(f"Ошибка при загрузке страницы: {e}")
    driver.quit()
    raise

# Поиск всех элементов с классом "projectCol_UFIvT" и "col_LxyFv"
try:
    logger.info("Поиск проектов...")
    projects = driver.find_elements(By.CSS_SELECTOR, 'div.projectCol_UFIvT')
    additional_projects = driver.find_elements(By.CSS_SELECTOR, 'div.col_LxyFv')
    all_projects = projects + additional_projects
    logger.info(f"Найдено {len(all_projects)} проектов.")
except Exception as e:
    logger.error(f"Ошибка при поиске проектов: {e}")
    driver.quit()
    raise

# Извлечение данных с основной страницы
project_data = []
try:
    logger.info("Извлечение данных с основной страницы...")
    for element in all_projects:
        # Извлечение названия ЖК
        try:
            title_element = element.find_element(By.CSS_SELECTOR, 'div.title_JOYuM')
            title = title_element.text.strip()
        except Exception as e:
            title = "Нет данных"
            logger.warning(f"Не удалось извлечь название ЖК: {e}")

        # Извлечение ссылки на проект
        try:
            link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
        except Exception as e:
            link = "Нет данных"
            logger.warning(f"Не удалось извлечь ссылку: {e}")

        # Добавление данных в список
        project_data.append({
            "Название ЖК": title,
            "Ссылка на проект": link
        })
    logger.info(f"Успешно извлечено {len(project_data)} записей.")
except Exception as e:
    logger.error(f"Ошибка при извлечении данных с основной страницы: {e}")
    driver.quit()
    raise

# Создание DataFrame для хранения данных
data = []

# Переход по каждой ссылке и извлечение текста
for project in project_data:
    link = project["Ссылка на проект"]
    title = project["Название ЖК"]

    try:
        logger.info(f"Переход на страницу проекта: {link}")
        driver.get(link)
        time.sleep(3)  # Ожидание загрузки страницы

        # Извлечение текста из элемента с классом "text_tPdzV"
        try:
            text_element = driver.find_element(By.CLASS_NAME, "text_tPdzV")
            text = text_element.text.strip()
            logger.info("Текст успешно извлечен.")
        except Exception as e:
            text = "Нет данных"
            logger.warning(f"Не удалось извлечь текст: {e}")

        # Добавление данных в список
        data.append({
            "Название ЖК": title,
            "Ссылка на проект": link,
            "Текст": text
        })
    except Exception as e:
        logger.error(f"Ошибка при обработке страницы проекта {link}: {e}")
        continue

# Закрытие драйвера
logger.info("Завершение работы драйвера...")
driver.quit()

# Создание DataFrame
try:
    logger.info("Создание DataFrame...")
    df = pd.DataFrame(data)
    logger.info("DataFrame успешно создан.")
except Exception as e:
    logger.error(f"Ошибка при создании DataFrame: {e}")
    raise

# Сохранение данных в файл Excel
output_file = "a101_projectssss.xlsx"
try:
    logger.info(f"Сохранение данных в файл {output_file}...")
    df.to_excel(output_file, index=False)
    logger.info(f"Данные успешно сохранены в файл {output_file}.")
except Exception as e:
    logger.error(f"Ошибка при сохранении данных в файл: {e}")
    raise
