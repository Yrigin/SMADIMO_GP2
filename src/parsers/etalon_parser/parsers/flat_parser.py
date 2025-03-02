import logging
from playwright.sync_api import Page

from parsers.base_parser import BaseParser
from extractors.apartment_extractor import extract_apartment_details
from extractors.features_extractor import parse_features_component
from utils.browser_utils import wait_page, check_and_solve_captcha
from utils.human_behavior import simulate_human_behavior, random_delay

logger = logging.getLogger("StealthyParser")

class FlatParser(BaseParser):
    """Парсер для квартир сайта Etalon Group"""
    
    def __init__(self, max_workers=4):
        super().__init__(max_workers)
    
    def parse_page(self, page: Page, url: str):
        """
        Парсит страницу с квартирой
        
        Args:
            page: Объект страницы Playwright
            url: URL страницы для парсинга
            
        Returns:
            dict: Данные о квартире
        """
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