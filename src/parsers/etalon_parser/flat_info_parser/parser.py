import re
import json
from tqdm import tqdm
import logging
import os
from playwright.sync_api import sync_playwright, Page, Browser
import time
import json
import os
import logging
import sys
import random
from datetime import datetime
import pandas as pd

# Настройка цветного вывода в терминал
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[92m',  # зеленый
        'WARNING': '\033[93m',  # желтый
        'ERROR': '\033[91m',  # красный
        'DEBUG': '\033[94m',  # синий
        'RESET': '\033[0m'  # сброс цвета
    }
    
    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{log_message}{self.COLORS['RESET']}"

# Настройка логирования
logger = logging.getLogger("StealthyParser")
logger.setLevel(logging.INFO)

# Обработчик для вывода в файл
file_handler = logging.FileHandler("extraction.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Обработчик для вывода в консоль с цветами
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Отображает прогресс-бар в консоли"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total: 
        sys.stdout.write('\n')

def simulate_human_behavior(page: Page):
    """Имитирует поведение реального пользователя"""
    logger.info("🧠 Имитация человеческого поведения...")
    
    # Случайные движения мыши
    for _ in range(random.randint(3, 7)):
        x = random.randint(100, 1500)
        y = random.randint(100, 700)
        page.mouse.move(x, y, steps=random.randint(5, 10))  # Плавное движение мыши
        random_delay(0.1, 0.5)
    
    # Случайные прокрутки с разной скоростью
    scroll_amount = random.randint(300, 700)
    logger.debug(f"Прокрутка вниз на {scroll_amount}px")
    page.mouse.wheel(0, scroll_amount)
    random_delay(0.1, 0.5)
    
    # С вероятностью 40% прокручиваем немного вверх, как будто что-то заинтересовало
    if random.random() < 0.4:
        back_scroll = random.randint(100, 300)
        logger.debug(f"Прокрутка вверх на {back_scroll}px")
        page.mouse.wheel(0, -back_scroll)
        random_delay(0.1, 0.5)
    
    # Иногда выделяем текст (с вероятностью 20%)
    if random.random() < 0.2:
        text_elements = page.query_selector_all("p, h1, h2, h3, span, a")
        if text_elements:
            element = random.choice(text_elements)
            try:
                element.click(click_count=random.choice([1, 3]))  # Одиночный или тройной клик
                random_delay(0.1, 0.5)
                page.keyboard.press("Escape")  # Снимаем выделение
            except:
                pass  # Игнорируем ошибки при клике
    
    # Иногда "думаем" дольше (с вероятностью 30%)
    if random.random() < 0.3:
        random_delay(0.1, 0.5)
    
    # Имитация изучения контента
    page.mouse.wheel(0, random.randint(100, 400))
    random_delay(0.1, 0.5)

def random_delay(min_seconds=1, max_seconds=5):
    """Создает случайную задержку между действиями"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def load_cookies(context):
    """Загружает cookies из файла, если он существует"""
    cookies_file = 'etalon_cookies.json'
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
                logger.info(f"🍪 Загружено {len(cookies)} cookies из файла")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при загрузке cookies: {e}")
    return False

def save_cookies(context):
    """Сохраняет cookies в файл для последующего использования"""
    cookies = context.cookies()
    with open('etalon_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False)
    logger.info(f"🍪 Сохранено {len(cookies)} cookies в файл")

def check_and_solve_captcha(page):
    """Проверяет наличие CAPTCHA и пытается решить её"""
    captcha_selectors = [
        'iframe[src*="recaptcha"]',
        'iframe[src*="captcha"]',
        'div.g-recaptcha',
        'div[class*="captcha"]',
        'img[src*="captcha"]'
    ]
    
    for selector in captcha_selectors:
        if page.is_visible(selector):
            logger.warning(f"⚠️ Обнаружена CAPTCHA: {selector}")
            page.screenshot(path="captcha_detected.png")
            input("CAPTCHA обнаружена! Решите её вручную и нажмите Enter для продолжения...")
            return True
    
    return False

def extract_property_links(page: Page):
    """Извлекает все ссылки на объекты недвижимости с учетом правильной структуры"""
    logger.info("🔍 Извлекаем ссылки на объекты недвижимости...")
    
    # Список селекторов для поиска ссылок на объекты, включая правильный селектор
    selectors = [
        'a[href*="/msk/choose/"]',  # Правильный селектор на основе предоставленного HTML
        'div.bg-white.relative > a',  # Альтернативный селектор по структуре
        '.bg-white a'  # Более общий селектор
    ]
    
    all_links = set()  # Используем множество для исключения дубликатов
    
    # Пробуем каждый селектор
    for selector in selectors:
        elements = page.query_selector_all(selector)
        logger.info(f"Селектор '{selector}' нашел {len(elements)} элементов")
        
        for element in elements:
            href = element.get_attribute('href')
            if href:
                # Преобразуем относительные ссылки в абсолютные
                full_url = 'https://etalongroup.ru' + href if href.startswith('/') else href
                all_links.add(full_url)
    
    
    # Проверяем количество найденных ссылок
    logger.info(f"Всего найдено {len(all_links)} уникальных ссылок на объекты")
    
    return list(all_links)


def wait_page(results_page):
    # Используйте более надежную комбинацию состояний загрузки:
    try:
        # Ждем только основную загрузку страницы (DOMContentLoaded и load events)
        results_page.wait_for_load_state("load", timeout=30000)
        logger.info("✅ Базовая загрузка страницы завершена")
        
        # Даем дополнительное время для загрузки JavaScript-контента
        random_delay(0.5, 2)
        
        # Дополнительно ждем появления конкретных элементов на странице
        # вместо ожидания полного прекращения сетевой активности
        try:
            results_page.wait_for_selector('a[href*="/msk/object/"]', timeout=10000)
            logger.info("✅ Найдены элементы с объектами недвижимости")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось дождаться появления элементов с объектами: {e}")
            # Продолжаем выполнение, даже если элементы не найдены
        
        logger.info(f"✅ Новая страница загружена: {results_page.url}")
    except Exception as e:
        logger.warning(f"⚠️ Предупреждение при загрузке страницы: {e}")
        # Делаем скриншот для отладки
        try:
            results_page.screenshot(path="page_load_warning.png")
        except:
            pass
        
        # Продолжаем выполнение, даже если произошла ошибка при ожидании загрузки
        logger.info("Продолжаем работу с частично загруженной страницей")


def extract_apartment_details(page):
    """Извлекает детальную информацию о квартире из открытой страницы"""
    
    apartment_data = {}
    
    # Основная информация о квартире
    title = page.query_selector("h4.th-h3.text-charcoal")
    if title:
        title_text = title.inner_text()
        # Извлекаем номер квартиры и площадь из заголовка
        apartment_data["title"] = title_text
        room_match = re.search(r'(\d+)-комн', title_text)
        apartment_data["rooms"] = room_match.group(1) if room_match else None
        
        number_match = re.search(r'№(\d+)', title_text)
        apartment_data["number"] = number_match.group(1) if number_match else None
        
        area_match = re.search(r'(\d+(?:,\d+)?)\s*м²', title_text)
        apartment_data["area"] = area_match.group(1).replace(',', '.') if area_match else None
    
    # Цена
    price_elem = page.query_selector("p.th-h3.text-scarlet")
    if price_elem:
        price_text = price_elem.inner_text()
        clean_price = re.sub(r'[^\d]', '', price_text)
        apartment_data["price"] = clean_price
    
    # Цена за м²
    price_per_meter_elem = page.query_selector("div.th-b1-regular.text-cruella")
    if price_per_meter_elem:
        price_per_meter_text = price_per_meter_elem.inner_text()
        clean_price_per_meter = re.sub(r'[^\d]', '', price_per_meter_text)
        apartment_data["price_per_meter"] = clean_price_per_meter
    
    # Срок сдачи
    completion_date_elem = page.query_selector("div.u-badge__content span.th-b1-regular")
    if completion_date_elem:
        apartment_data["completion_date"] = completion_date_elem.inner_text().strip()
    
    # Информация о проекте, метро и адресе
    project_details = {}
    info_rows = page.query_selector_all("section.flex.flex-col.gap-2.pb-4 > div")
    
    for row in info_rows:
        # Находим ключ и значение в каждой строке
        key_elem = row.query_selector("p:first-child")
        value_elem = row.query_selector("p:last-child")
        
        if key_elem and value_elem:
            key = key_elem.inner_text().strip()
            
            # Для поля "Проект" значение находится внутри span
            if key == "Проект":
                project_span = row.query_selector("span.th-b1-bold")
                value = project_span.inner_text().strip() if project_span else value_elem.inner_text().strip()
            else:
                value = value_elem.inner_text().strip()
            
            project_details[key] = value
    
    apartment_data["details"] = project_details
    
    # Получаем размеры комнат (нужно нажать на кнопку "Показать размеры комнат")
    show_room_sizes_button = page.query_selector("div.flex.flex-row.items-center.gap-1.th-b1-bold.text-charcoal.cursor-pointer")
    if show_room_sizes_button:
        show_room_sizes_button.click()
        # Ждем, пока раскроется секция с размерами
        page.wait_for_timeout(500)
        
        room_sizes = {}
        size_rows = page.query_selector_all("section.overflow-hidden div.flex.flex-row")
        
        for row in size_rows:
            room_name_elem = row.query_selector("p:first-child")
            room_size_elem = row.query_selector("p.flex-grow.text-right")
            
            if room_name_elem and room_size_elem:
                room_name = room_name_elem.inner_text().strip()
                room_size_text = room_size_elem.inner_text().strip()
                size_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', room_size_text)
                room_size = size_match.group(1).replace(',', '.') if size_match else room_size_text
                room_sizes[room_name] = room_size
        
        apartment_data["room_sizes"] = room_sizes
    
    # Ссылка на презентацию
    presentation_link = page.query_selector('a[href*="pdfflat"]')
    if presentation_link:
        apartment_data["presentation_url"] = presentation_link.get_attribute("href")
    
    return apartment_data

def parse_features_component(page):
    """
    Парсит компонент "Особенности" со всеми вкладками
    Возвращает словарь с данными всех разделов
    """
    features_data = {}
    
    try:
        # Проверяем наличие компонента "Особенности" на странице
        features_title = page.query_selector("p.th-h2:has-text('Особенности')")
        
        if not features_title:
            print("Компонент 'Особенности' не найден на странице")
            return features_data
        
        # Находим все вкладки
        tabs = page.query_selector_all("button.v-tab")
        
        if not tabs:
            print("Вкладки в компоненте 'Особенности' не найдены")
            return features_data
        
        print(f"Найдено {len(tabs)} вкладок в компоненте 'Особенности'")
        
        # Обходим все вкладки
        for i, tab in enumerate(tabs):
            try:
                # Получаем название вкладки
                tab_title_element = tab.query_selector("span.u-tab__text")
                if tab_title_element:
                    tab_title = tab_title_element.inner_text().strip()
                else:
                    tab_title = f"Вкладка {i+1}"
                
                print(f"Обрабатываем вкладку: {tab_title}")
                
                # ВАЖНОЕ ИСПРАВЛЕНИЕ: Ждем, пока содержимое вкладки полностью отрендерится
                # Используем явное ожидание появления элемента в активной вкладке
                try:
                    # Ожидаем появления контейнера с содержимым в активной вкладке
                    page.wait_for_selector("div.v-window-item--active div.bg-light-gray", timeout=5000)
                    
                    # Дополнительно ждем появления заголовка в активной вкладке
                    page.wait_for_selector("div.v-window-item--active p.th-h3", timeout=5000)
                    
                    # Дополнительно ждем появления секции с текстом
                    page.wait_for_selector("div.v-window-item--active section", timeout=5000)
                    
                    # Даем дополнительное время для полного рендеринга
                    page.wait_for_timeout(500)
                except Exception as wait_error:
                    print(f"Предупреждение: Не удалось дождаться загрузки содержимого вкладки: {str(wait_error)}")
                

                # Кликаем на вкладку для активации содержимого
                tab.click()
                
                # Даем время на загрузку содержимого
                page.wait_for_timeout(1000)
                
                # Создаем словарь для данных текущей вкладки
                tab_data = {}
                
                # Используем JavaScript для извлечения данных по точной структуре:
                # title (p.th-h3) после которого идет section с description
                # Используем JavaScript для извлечения данных, учитывая, что есть несколько активных элементов
                result = page.evaluate("""(tabName) => {
                    // Находим контейнер с особенностями по заголовку
                    const featuresSection = Array.from(document.querySelectorAll('p.th-h2'))
                        .find(el => el.textContent.trim() === 'Особенности')
                        ?.closest('div.max-w-\\\\[1210px\\\\]');
                    
                    if (!featuresSection) return { title: '', description: '', images: [] };
                    
                    // Находим активную вкладку ВНУТРИ секции особенностей
                    const activeTab = featuresSection.querySelector('.v-window-item--active');
                    if (!activeTab) return { title: '', description: '', images: [] };
                    
                    // Находим блок с информацией (div с классом bg-light-gray)
                    const infoBlock = activeTab.querySelector('div.bg-light-gray');
                    if (!infoBlock) return { title: '', description: '', images: [] };
                    
                    // Находим заголовок (p.th-h3)
                    const titleElem = infoBlock.querySelector('p.th-h3');
                    const title = titleElem ? titleElem.textContent.trim() : tabName;
                    
                    // Находим секцию с описанием, которая идет после заголовка
                    const sectionElem = infoBlock.querySelector('section');
                    
                    // Извлекаем текст из всех параграфов внутри section
                    let description = '';
                    if (sectionElem) {
                        // Собираем текст из всех параграфов, исключая контейнеры
                        const paragraphs = Array.from(sectionElem.querySelectorAll('p'))
                            .filter(p => !p.classList.contains('flex') || !p.querySelector('p'));
                        
                        const textArray = [];
                        for (const p of paragraphs) {
                            // Проверяем, является ли это непосредственным текстовым параграфом
                            if (p.childElementCount === 0 || 
                                (p.childElementCount > 0 && !p.querySelector('p'))) {
                                const text = p.textContent.trim();
                                if (text) textArray.push(text);
                            }
                        }
                        
                        description = textArray.join('\\n\\n');
                    }
                    
                    // Находим все изображения в активной вкладке
                    const images = activeTab.querySelectorAll('img.v-img__img--cover');
                    const imageUrls = Array.from(images)
                        .map(img => img.getAttribute('src'))
                        .filter(src => src);
                    
                    return {
                        title: title,
                        description: description,
                        images: imageUrls
                    };
                }""", tab_title)
                
                # Создаем словарь для данных текущей вкладки
                tab_data = result if result else {"title": tab_title, "description": "", "images": []}
                
                # Добавляем данные вкладки в общий словарь
                features_data[tab_title] = tab_data
                
                print(f"Для вкладки '{tab_title}' извлечено:")
                print(f"  - Заголовок: {tab_data.get('title', 'Не найден')}")
                desc = tab_data.get('description', 'Не найдено')
                print(f"  - Описание: {desc[:50]}..." if len(desc) > 50 else f"  - Описание: {desc}")
                print(f"  - Изображения: {len(tab_data.get('images', []))}")
            
            except Exception as e:
                print(f"Ошибка при обработке вкладки {i+1}: {str(e)}")
        
    except Exception as e:
        print(f"Ошибка при парсинге компонента 'Особенности': {str(e)}")
    
    return features_data

def parse_apartment_page(page: Page, url):
        # Переходим на страницу квартиры
        page.goto(url, timeout=60000)

        wait_page(page)

        # Имитируем человеческое поведение сразу после загрузки
        random_delay(0.5, 2)
        simulate_human_behavior(page)
        
        # Проверяем наличие CAPTCHA
        if check_and_solve_captcha(page):
            logger.info("CAPTCHA решена, продолжаем...")

        # Извлекаем данные
        apartment_data = extract_apartment_details(page)

        # Добавляем URL в данные
        apartment_data["url"] = url

        # Проверяем наличие компонента "Особенности" и парсим его
        features_section = page.query_selector("p.th-h2.text-charcoal:has-text('Особенности')")
        if features_section:
            # Парсим компонент "Особенности"
            features_data = parse_features_component(page)
            if features_data:
                apartment_data["features"] = features_data

        return apartment_data

def browse() -> Browser:
    logger.info("=" * 60)
    logger.info(f"🥷 НАЧАЛО СКРЫТОГО ПАРСИНГА: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Список User-Agent для ротации
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
    ]
    
    # Случайные размеры окна
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1366, "height": 768}
    ]
    
    # Явный путь к Yandex Browser на macOS
    yandex_path = "/Applications/Yandex.app/Contents/MacOS/Yandex"
    
    # Проверяем существование браузера по указанному пути
    if not os.path.exists(yandex_path):
        logger.warning(f"Yandex Browser не найден по пути: {yandex_path}")
        logger.info("Проверяем альтернативные пути...")
        
        # Альтернативные пути к Yandex Browser
        alternative_paths = [
            "/Applications/Yandex Browser.app/Contents/MacOS/Yandex Browser",
            os.path.expanduser("~/Applications/Yandex.app/Contents/MacOS/Yandex"),
            os.path.expanduser("~/Applications/Yandex Browser.app/Contents/MacOS/Yandex Browser")
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                yandex_path = path
                logger.info(f"Найден Yandex Browser: {yandex_path}")
                break
        else:
            logger.error("Yandex Browser не найден ни в одном из ожидаемых мест")
            custom_path = input("Введите полный путь к исполняемому файлу Yandex Browser: ")
            if os.path.exists(custom_path):
                yandex_path = custom_path
            else:
                logger.error(f"Путь не найден: {custom_path}")
                return
    
    logger.info(f"Используем Yandex Browser: {yandex_path}")

    with sync_playwright() as p:
        # Выбираем случайный User-Agent
        selected_user_agent = random.choice(user_agents)
        selected_viewport = random.choice(viewports)
        
        logger.info(f"🎭 Используем User-Agent: {selected_user_agent}")
        logger.info(f"📐 Размер окна: {selected_viewport['width']}x{selected_viewport['height']}")
        
        browser = p.chromium.launch(
            headless=True,
            executable_path=yandex_path,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",  # Скрывает автоматизацию
                "--disable-extensions"
            ]
        ) 
        
        # Создаем контекст с выбранными параметрами
        context = browser.new_context(
            user_agent=selected_user_agent,
            viewport=selected_viewport,
            locale=random.choice(["ru-RU", "en-US"]),
            timezone_id="Europe/Moscow"
        )
        
        # Загружаем cookies если есть
        has_cookies = load_cookies(context)
        
        # Создаем страницу
        page = context.new_page()
        
        # Устанавливаем скрипты для обхода обнаружения автоматизации
        page.add_init_script("""
            // Перезаписываем свойства navigator для маскировки автоматизации
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // Скрываем другие признаки автоматизации
            if (window.navigator.plugins) {
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            }
            
            // Добавляем фейковые языки
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en'],
            });
            
            // Скрываем Chrome
            window.chrome = {
                runtime: {},
            };
        """)

         # Используем случайную задержку перед открытием сайта
        start_delay = random_delay(0.5, 2)
        logger.debug(f"Задержка перед открытием сайта: {start_delay:.2f}с")

        # Загружаем список URL
        urls = json.load(open("link_extractor/extracted_links.json", "r", encoding="utf-8"))

        # Проверяем, существует ли файл с результатами
        if os.path.exists("result.csv"):
            # Загружаем существующие данные
            df = pd.read_csv("result.csv")
            print(f"Загружен существующий файл с {len(df)} записями")
            
            # Получаем список уже обработанных URL
            processed_urls = df['url'].tolist()
            
            # Отфильтровываем только необработанные URL
            urls_to_process = [url for url in urls if url not in processed_urls]
            print(f"Осталось обработать {len(urls_to_process)} из {len(urls)} URL")
        else:
            # Если файла нет, создаем пустой DataFrame и обрабатываем все URL
            df = pd.DataFrame()
            urls_to_process = urls
            print(f"Будут обработаны все {len(urls)} URL")
        
        # Если нет URL для обработки, завершаем работу
        if not urls_to_process:
            print("Все URL уже обработаны")
            return df


        for url in tqdm(urls_to_process, desc="Парсинг квартир"):
            try:
                data = parse_apartment_page(page, url)

                # Преобразуем данные в DataFrame
                new_df = pd.DataFrame([data])

                # Добавляем новые данные к существующим
                df = pd.concat([df, new_df], ignore_index=True)

                # Сохраняем обновленный DataFrame после каждой обработанной квартиры
                df.to_csv("result.csv", index=False, encoding="utf-8-sig")
            except Exception as e:
                print(f"Ошибка при обработке URL {url}: {str(e)}")

        save_cookies(context)

        browser.close()


# Пример использования
if __name__ == "__main__":
    browse()