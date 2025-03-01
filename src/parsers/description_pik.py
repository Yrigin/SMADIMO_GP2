from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.FileHandler("scraping.log", encoding="utf-8"),  # Логи в файл
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

# Открытие страницы со списком проектов
try:
    logger.info("Открытие страницы со списком проектов...")
    driver.get("https://www.pik.ru/projects")
    logger.info("Страница успешно открыта.")
except Exception as e:
    logger.error(f"Ошибка при открытии страницы: {e}")
    driver.quit()
    raise

# Ожидание загрузки страницы
time.sleep(5)

# Поиск всех ссылок на проекты
try:
    logger.info("Поиск ссылок на проекты...")
    project_links = driver.find_elements(By.CSS_SELECTOR, 'a.styles__ProjectCard-uyo9w7-0.iGEdxU')
    logger.info(f"Найдено {len(project_links)} ссылок на проекты.")
except Exception as e:
    logger.error(f"Ошибка при поиске ссылок на проекты: {e}")
    driver.quit()
    raise

# Список для хранения данных
data = []

# Переход по каждой ссылке и извлечение данных
for i, link in enumerate(project_links):
    try:
        logger.info(f"Обработка проекта {i + 1}/{len(project_links)}...")
        
        # Получаем URL проекта
        project_url = link.get_attribute("href")
        logger.info(f"URL проекта: {project_url}")
        
        # Открываем новую вкладку и переходим по ссылке
        driver.execute_script("window.open('');")  # Открыть новую вкладку
        driver.switch_to.window(driver.window_handles[1])  # Переключиться на новую вкладку
        driver.get(project_url)  # Перейти по ссылке проекта
        logger.info("Переход на страницу проекта выполнен.")
        
        # Ожидание загрузки страницы
        time.sleep(3)
        
        # Извлечение данных
        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.styles__Title-fqnz85-2.iXrWwJ').text
            logger.info(f"Заголовок проекта: {title}")
        except Exception as e:
            title = "Нет данных"
            logger.warning(f"Не удалось извлечь заголовок: {e}")
        
        try:
            description = driver.find_element(By.CSS_SELECTOR, 'p.sc-hxhCaM.deNMct').text
            logger.info(f"Описание проекта: {description}")
        except Exception as e:
            description = "Нет данных"
            logger.warning(f"Не удалось извлечь описание: {e}")
        
        # Извлечение текста из элементов с классами p.sc-feNupb.bscsLW и span.sc-feNupb.bscsLW
        try:
            additional_text_p = driver.find_element(By.CSS_SELECTOR, 'p.sc-feNupb.bscsLW').text
            logger.info(f"Дополнительный текст (p): {additional_text_p}")
        except Exception as e:
            additional_text_p = "Нет данных"
            logger.warning(f"Не удалось извлечь дополнительный текст (p): {e}")
        
        try:
            additional_text_span = driver.find_element(By.CSS_SELECTOR, 'span.sc-feNupb.bscsLW').text
            logger.info(f"Дополнительный текст (span): {additional_text_span}")
        except Exception as e:
            additional_text_span = "Нет данных"
            logger.warning(f"Не удалось извлечь дополнительный текст (span): {e}")
        
        # Сохранение данных в список
        data.append({
            "Ссылка": project_url,
            "Заголовок": title,
            "Описание": description,
            "Дополнительный текст (p)": additional_text_p,
            "Дополнительный текст (span)": additional_text_span
        })
        
        # Закрытие вкладки и возврат к списку проектов
        driver.close()  # Закрыть текущую вкладку
        driver.switch_to.window(driver.window_handles[0])  # Вернуться к основной вкладке
        logger.info("Закрытие вкладки проекта и возврат к списку проектов.")
    
    except Exception as e:
        logger.error(f"Ошибка при обработке проекта {i + 1}: {e}")
        continue

# Закрытие драйвера
try:
    logger.info("Завершение работы драйвера...")
    driver.quit()
    logger.info("Драйвер успешно закрыт.")
except Exception as e:
    logger.error(f"Ошибка при закрытии драйвера: {e}")

# Создание DataFrame
try:
    logger.info("Создание DataFrame...")
    df = pd.DataFrame(data)
    logger.info("DataFrame успешно создан.")
except Exception as e:
    logger.error(f"Ошибка при создании DataFrame: {e}")
    raise

# Сохранение данных в Excel
try:
    logger.info("Сохранение данных в Excel...")
    df.to_excel("projects_data.xlsx", index=False)
    logger.info("Данные успешно сохранены в projects_data.xlsx.")
except Exception as e:
    logger.error(f"Ошибка при сохранении данных в Excel: {e}")
    raise

# Вывод данных в консоль
print(df)
