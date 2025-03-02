import re
import logging
from playwright.sync_api import Page

logger = logging.getLogger("StealthyParser")

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