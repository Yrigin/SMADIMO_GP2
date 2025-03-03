import os
import random
import logging
from playwright.sync_api import sync_playwright, Page

logger = logging.getLogger("StealthyParser")

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

def wait_page(page):
    """Ожидает загрузку страницы с надежной стратегией ожидания"""
    try:
        # Ждем только основную загрузку страницы (DOMContentLoaded и load events)
        page.wait_for_load_state("load", timeout=30000)
        logger.info("✅ Базовая загрузка страницы завершена")
        
        # Даем дополнительное время для загрузки JavaScript-контента
        from utils.human_behavior import random_delay
        random_delay(0.5, 2)
        
        # Дополнительно ждем появления конкретных элементов на странице
        try:
            page.wait_for_selector('a[href*="/msk/object/"]', timeout=10000)
            logger.info("✅ Найдены элементы с объектами недвижимости")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось дождаться появления элементов с объектами: {e}")
        
        logger.info(f"✅ Новая страница загружена: {page.url}")
    except Exception as e:
        logger.warning(f"⚠️ Предупреждение при загрузке страницы: {e}")
        # Делаем скриншот для отладки
        try:
            page.screenshot(path="page_load_warning.png")
        except:
            pass
        
        logger.info("Продолжаем работу с частично загруженной страницей")

def find_browser_path():
    """Находит путь к Yandex Browser"""
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
                return None
    
    logger.info(f"Используем Yandex Browser: {yandex_path}")
    return yandex_path

def setup_browser_context(playwright, headless=True):
    """Настраивает браузер и контекст с антидетект-настройками"""
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
    
    yandex_path = find_browser_path()
    if not yandex_path:
        return None, None
    
    # Выбираем случайный User-Agent
    selected_user_agent = random.choice(user_agents)
    selected_viewport = random.choice(viewports)
    
    logger.info(f"🎭 Используем User-Agent: {selected_user_agent}")
    logger.info(f"📐 Размер окна: {selected_viewport['width']}x{selected_viewport['height']}")
    
    browser = playwright.chromium.launch(
        headless=headless,
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
    
    return browser, context

def setup_page_stealth(page):
    """Настраивает страницу для обхода обнаружения автоматизации"""
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
    return page