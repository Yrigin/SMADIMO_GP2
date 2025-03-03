import logging
from playwright.sync_api import Page

logger = logging.getLogger("StealthyParser")

def extract_property_links(page: Page):
    """
    Извлекает все ссылки на объекты недвижимости с учетом правильной структуры
    
    Args:
        page: Объект страницы Playwright
        
    Returns:
        list: Список ссылок на объекты недвижимости
    """
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