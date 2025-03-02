from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Настройка опций для Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки SSL

# Автоматическая установка ChromeDriver
service = Service(ChromeDriverManager().install())

# Инициализация драйвера
driver = webdriver.Chrome(service=service, options=chrome_options)

# Переход на главную страницу
main_url = "https://www.ingrad.ru/#projects"
driver.get(main_url)
time.sleep(5)  # Ожидание загрузки страницы

# Сбор всех ссылок на проекты
project_links = []
projects = driver.find_elements(By.CSS_SELECTOR, 'li.big-project-card a.big-project-card__max-link')
for project in projects:
    link = project.get_attribute("href")
    project_links.append(link)

print(f"Найдено {len(project_links)} проектов.")

# Сбор данных с каждой страницы проекта
project_data = []

for link in project_links:
    print(f"Переход на страницу проекта: {link}")
    driver.get(link)
    time.sleep(3)  # Ожидание загрузки страницы

    # Поиск заголовка h1 с классом "hero-image__title"
    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1.hero-image__title').text
    except Exception as e:
        title = "Заголовок не найден"
        print(f"Ошибка при поиске заголовка: {e}")

    # Поиск текста в объекте div с классом "tabs-text__description"
    try:
        description = driver.find_element(By.CSS_SELECTOR, 'div.tabs-text__description').text
    except Exception as e:
        description = "Описание не найдено"
        print(f"Ошибка при поиске описания: {e}")

    # Сохранение данных
    project_data.append({
        "Ссылка": link,
        "Заголовок": title,
        "Описание": description
    })


driver.quit()


# Сохранение данных в CSV
df = pd.DataFrame(project_data)
df.to_csv("ingrad_description-02-03-2025.csv", index=False)
print("Данные сохранены в файл ingrad_description-02-03-2025.csv")
