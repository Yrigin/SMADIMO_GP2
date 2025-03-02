from playwright.sync_api import sync_playwright, Page
import time
import json
import os
import logging
import sys
import random
from datetime import datetime

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

def simulate_human_behavior(page):
    """Имитирует поведение реального пользователя"""
    logger.info("🧠 Имитация человеческого поведения...")
    
    # Случайные движения мыши
    for _ in range(random.randint(3, 7)):
        x = random.randint(100, 1500)
        y = random.randint(100, 700)
        page.mouse.move(x, y, steps=random.randint(5, 10))  # Плавное движение мыши
        time.sleep(random.uniform(0.3, 1.5))
    
    # Случайные прокрутки с разной скоростью
    scroll_amount = random.randint(300, 700)
    logger.debug(f"Прокрутка вниз на {scroll_amount}px")
    page.mouse.wheel(0, scroll_amount)
    time.sleep(random.uniform(1.0, 2.5))
    
    # С вероятностью 40% прокручиваем немного вверх, как будто что-то заинтересовало
    if random.random() < 0.4:
        back_scroll = random.randint(100, 300)
        logger.debug(f"Прокрутка вверх на {back_scroll}px")
        page.mouse.wheel(0, -back_scroll)
        time.sleep(random.uniform(0.7, 1.8))
    
    # Иногда выделяем текст (с вероятностью 20%)
    if random.random() < 0.2:
        text_elements = page.query_selector_all("p, h1, h2, h3, span, a")
        if text_elements:
            element = random.choice(text_elements)
            try:
                element.click(click_count=random.choice([1, 3]))  # Одиночный или тройной клик
                time.sleep(random.uniform(0.5, 1.2))
                page.keyboard.press("Escape")  # Снимаем выделение
            except:
                pass  # Игнорируем ошибки при клике
    
    # Иногда "думаем" дольше (с вероятностью 30%)
    if random.random() < 0.3:
        thinking_time = random.uniform(2.0, 4.0)
        logger.debug(f"Пауза на {thinking_time:.1f} секунд")
        time.sleep(thinking_time)
    
    # Имитация изучения контента
    page.mouse.wheel(0, random.randint(100, 400))
    time.sleep(random.uniform(0.5, 1.5))

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
        random_delay(3, 5)
        
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

def extract_data_with_yandex():
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
        try:
            # Выбираем случайный User-Agent
            selected_user_agent = random.choice(user_agents)
            selected_viewport = random.choice(viewports)
            
            logger.info(f"🎭 Используем User-Agent: {selected_user_agent}")
            logger.info(f"📐 Размер окна: {selected_viewport['width']}x{selected_viewport['height']}")
            
            # Запускаем браузер с улучшенными настройками против обнаружения
            browser = p.chromium.launch(
                headless=False,  # Показываем браузер для наглядности
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
            
            logger.info("🌐 Открываем сайт etalongroup.ru/msk/...")
            
            # Используем случайную задержку перед открытием сайта
            start_delay = random_delay(1, 3)
            logger.debug(f"Задержка перед открытием сайта: {start_delay:.2f}с")
            
            # Открываем страницу
            page.goto("https://etalongroup.ru/choose/", timeout=60000)
            
            # Имитируем человеческое поведение сразу после загрузки
            random_delay(3, 6)
            simulate_human_behavior(page)
            
            # Проверяем наличие CAPTCHA
            if check_and_solve_captcha(page):
                logger.info("CAPTCHA решена, продолжаем...")
            
            # Сохраняем HTML страницы
            with open("initial_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            save_cookies(context)
            

            logger.info("🔍 Ищем кнопки 'Показать еще'...")
            
            counter = 0
            max_clicks = 30
            
            # Функция для поиска кнопки "Показать еще" различными способами
            def find_show_more_button():
                # 1. Ищем по точному классу (на основе предоставленного HTML)
                exact_selector = 'button.u-btn.u-btn--variant-flat.u-btn--density-default.u-btn--width-content.th-b1-medium:has-text("Показать еще")'
                if page.is_visible(exact_selector):
                    return exact_selector
                
                # 2. Ищем по содержимому текста
                text_selector = 'button:has-text("Показать еще")'
                if page.is_visible(text_selector):
                    return text_selector
                
                # 3. Ищем по частичным классам
                class_selector = 'button.u-btn--width-content:has-text("Показать еще")'
                if page.is_visible(class_selector):
                    return class_selector
                
                # 4. Ищем по содержимому span
                span_selector = 'button .u-btn__content:has-text("Показать еще")'
                if page.query_selector(span_selector):
                    button = page.query_selector(span_selector).evaluate('node => node.closest("button")')
                    if button:
                        return span_selector
                
                # 5. Ищем по XPath
                xpath_selector = "//button[.//span[contains(text(), 'Показать еще')]]"
                if page.is_visible(f"xpath={xpath_selector}"):
                    return f"xpath={xpath_selector}"
                
                # 6. Ищем более общим способом
                general_xpath = "//button[contains(., 'Показать еще')]"
                if page.is_visible(f"xpath={general_xpath}"):
                    return f"xpath={general_xpath}"
                
                return None
            
            # Функция для прокрутки и поиска кнопки
            def scroll_and_find_button():
                # Сначала ищем без прокрутки
                button = find_show_more_button()
                if button:
                    return button
                
                # Если не нашли, прокручиваем и ищем
                logger.info("Прокручиваем страницу для поиска кнопки...")
                
                # Прокручиваем до конца страницы
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)

                page.screenshot(path="first_scroll.png")
                
                # Ищем снова
                button = find_show_more_button()
                if button:
                    return button
                
                # Если все еще не нашли, прокручиваем еще немного вверх
                # (кнопка может быть скрыта под фиксированными элементами)
                page.evaluate("window.scrollBy(0, -1000)")
                page.wait_for_timeout(500)

                page.screenshot(path="second_scroll.png")
                
                return find_show_more_button()
            
            # Визуальная отладка - выделим все кнопки на странице
            def highlight_all_buttons():
                logger.info("Подсвечиваем все кнопки на странице для отладки...")
                page.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button');
                        buttons.forEach(button => {
                            button.style.border = '3px solid red';
                            
                            // Добавляем атрибуты для отладки
                            const text = button.textContent;
                            button.setAttribute('data-debug', text.trim());
                            
                            // Добавляем клик по всем кнопкам
                            button.onclick = function() {
                                console.log('Clicked button:', this.textContent);
                            }
                        });
                    }
                """)
                page.screenshot(path="highlighted_buttons.png")
            
            # Пытаемся найти и нажать кнопку "Показать еще"
            while counter < max_clicks:
                # Подсвечиваем кнопки, если это первая итерация или если не нашли кнопку
                if counter == 0:
                    highlight_all_buttons()
                
                # Ищем кнопку с прокруткой
                button_selector = scroll_and_find_button()
                
                if button_selector:
                    logger.info(f"👆 Нажимаем кнопку 'Показать еще' ({counter + 1}/{max_clicks}) с селектором: {button_selector}")
                    
                    try:
                        # Делаем скриншот перед нажатием
                        page.screenshot(path=f"before_click_{counter+1}.png")
                        
                        # Нажимаем на кнопку
                        if button_selector.startswith("xpath="):
                            # Если XPath, используем evaluate для клика
                            page.evaluate(f"""
                                () => {{
                                    const button = document.evaluate(
                                        "{button_selector.replace('xpath=', '')}", 
                                        document, 
                                        null, 
                                        XPathResult.FIRST_ORDERED_NODE_TYPE
                                    ).singleNodeValue;
                                    if (button) button.click();
                                }}
                            """)
                        else:
                            # Иначе используем стандартный метод клика
                            page.click(button_selector)
                        
                        # Ждем загрузки контента
                        page.wait_for_timeout(3000)
                        
                        # Делаем скриншот после нажатия
                        page.screenshot(path=f"after_click_{counter+1}.png")
                        
                        counter += 1
                        print_progress_bar(counter, max_clicks, prefix='Загрузка объектов:', suffix='Загружено', length=40)
                    except Exception as e:
                        logger.warning(f"Ошибка при нажатии кнопки: {e}")
                        
                        # Пробуем JavaScript-клик как запасной вариант
                        logger.info("Пробуем JavaScript-клик...")
                        try:
                            if button_selector.startswith("xpath="):
                                xpath = button_selector.replace("xpath=", "")
                                page.evaluate(f"""
                                    () => {{
                                        const button = document.evaluate(
                                            "{xpath}", 
                                            document, 
                                            null, 
                                            XPathResult.FIRST_ORDERED_NODE_TYPE
                                        ).singleNodeValue;
                                        if (button) button.click();
                                    }}
                                """)
                            else:
                                page.evaluate(f"""
                                    () => {{
                                        const button = document.querySelector('{button_selector}');
                                        if (button) button.click();
                                    }}
                                """)
                            page.wait_for_timeout(3000)
                            counter += 1
                        except Exception as js_e:
                            logger.error(f"JavaScript-клик тоже не сработал: {js_e}")
                            
                            # Если не получается нажать, делаем скриншот и пробуем следующую итерацию
                            page.screenshot(path=f"click_error_{counter+1}.png")
                            
                            # Прокручиваем страницу немного вниз
                            page.evaluate("window.scrollBy(0, 300)")
                            page.wait_for_timeout(1000)
                else:
                    # Если кнопка не найдена, делаем финальный скриншот и выходим из цикла
                    logger.info("✅ Кнопка 'Показать еще' не найдена - возможно, все объекты загружены")
                    page.screenshot(path="no_more_button.png")
                    break
            
            
            # Сохраняем финальный HTML
            logger.info("💾 Сохраняем HTML страницы со всеми загруженными объектами")
            html_content = page.content()
            with open("final_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info("🔍 Извлекаем ссылки на объекты недвижимости...")
            
            links = extract_property_links(page)
            logger.info(f"✅ Найдено {len(links)} объектов недвижимости")
            
            # Сохраняем результаты в JSON
            with open("extracted_links.json", "w", encoding="utf-8") as f:
                json.dump(links, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Успешно сохранено {len(links)} объектов в файл extracted_links.json")
        
            # Финальное сообщение
            logger.info("=" * 60)
            logger.info(f"✅ ПАРСИНГ ЗАВЕРШЕН: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # Даем возможность посмотреть на страницу перед закрытием
            logger.info("Нажмите Enter, чтобы закрыть браузер...")
            input()
            browser.close()
            
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}", exc_info=True)
            
            # Пытаемся сделать скриншот, если возможно
            try:
                if 'page' in locals() and page:
                    page.screenshot(path="error_screenshot.png")
                    logger.info("💾 Сохранен скриншот ошибки")
            except:
                logger.error("Не удалось сохранить скриншот ошибки")

if __name__ == "__main__":
    extract_data_with_yandex()