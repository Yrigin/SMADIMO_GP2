import logging
import os
import json
from datetime import datetime
from playwright.sync_api import Page

from parsers.base_parser import BaseParser
from utils.browser_utils import wait_page, check_and_solve_captcha
from utils.human_behavior import simulate_human_behavior, random_delay
from extractors.property_links_extractor import extract_property_links
from utils.ui_utils import print_progress_bar

logger = logging.getLogger("StealthyParser")

class LinkExtractorParser(BaseParser):
    """Парсер для извлечения ссылок на объекты недвижимости с сайта Etalon Group"""
    
    def __init__(self, max_workers=4, output_dir="link_extractor"):
        """
        Инициализирует парсер для извлечения ссылок
        
        Args:
            max_workers: Максимальное количество параллельных процессов
            output_dir: Директория для сохранения результатов
        """
        super().__init__(max_workers)
        self.output_dir = output_dir
        
        # Создаем директорию для результатов, если она не существует
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Создана директория для результатов: {output_dir}")
    
    def parse_page(self, page: Page, url: str):
        """
        Парсит страницу выбора квартир и извлекает ссылки на все объекты
        
        Args:
            page: Объект страницы Playwright
            url: URL страницы для парсинга
            
        Returns:
            dict: Данные о найденных ссылках
        """
        # Переходим на страницу выбора квартир
        page.goto(url, timeout=60000)
        wait_page(page)
        
        # Имитируем человеческое поведение сразу после загрузки
        random_delay(0.5, 1.5)
        simulate_human_behavior(page)
        
        # Проверяем наличие CAPTCHA
        if check_and_solve_captcha(page):
            logger.info("CAPTCHA решена, продолжаем...")
        
        # Сохраняем HTML страницы
        initial_html_path = os.path.join(self.output_dir, "initial_page.html")
        with open(initial_html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        
        # Нажимаем кнопку "Показать еще" несколько раз для загрузки всех объектов
        self._load_all_properties(page)
        
        # Сохраняем финальный HTML
        logger.info("💾 Сохраняем HTML страницы со всеми загруженными объектами")
        html_content = page.content()
        final_html_path = os.path.join(self.output_dir, "final_page.html")
        with open(final_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Извлекаем ссылки на объекты недвижимости
        links = extract_property_links(page)
        logger.info(f"✅ Найдено {len(links)} объектов недвижимости")
        
        # Сохраняем результаты в JSON
        json_path = os.path.join(self.output_dir, "extracted_links.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Успешно сохранено {len(links)} объектов в файл {json_path}")
        
        # Возвращаем результат
        return {
            "url": url,
            "extracted_links": len(links),
            "links": links,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _load_all_properties(self, page: Page):
        """
        Загружает все объекты недвижимости, нажимая кнопку "Показать еще"
        
        Args:
            page: Объект страницы Playwright
        """
        logger.info("🔍 Ищем кнопки 'Показать еще'...")
        
        counter = 0
        max_clicks = 1000
        
        # Визуальная отладка - выделим все кнопки на странице
        self._highlight_all_buttons(page)
        
        # Пытаемся найти и нажать кнопку "Показать еще"
        while counter < max_clicks:
            # Ищем кнопку с прокруткой
            button_selector = self._scroll_and_find_button(page)
            
            if button_selector:
                logger.info(f"👆 Нажимаем кнопку 'Показать еще' ({counter + 1}/{max_clicks}) с селектором: {button_selector}")
                
                try:
                    
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
                    page.wait_for_timeout(1000)
                    
                    # # Делаем скриншот после нажатия
                    # screenshot_path = os.path.join(self.output_dir, f"after_click_{counter+1}.png")
                    # page.screenshot(path=screenshot_path)
                    
                    counter += 1
                    print_progress_bar(counter, max_clicks, prefix='Загрузка объектов:', suffix='Загружено', length=40)

                    # Извлекаем ссылки на объекты недвижимости
                    links = extract_property_links(page)
                    logger.info(f"✅ Найдено {len(links)} объектов недвижимости")
                    
                    # Сохраняем результаты в JSON
                    json_path = os.path.join(self.output_dir, "extracted_links.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(links, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"💾 Успешно сохранено {len(links)} объектов в файл {json_path}")
                except Exception as e:
                    logger.warning(f"Ошибка при нажатии кнопки: {e}")
            else:
                # Если кнопка не найдена, делаем финальный скриншот и выходим из цикла
                logger.info("✅ Кнопка 'Показать еще' не найдена - возможно, все объекты загружены")
                screenshot_path = os.path.join(self.output_dir, "no_more_button.png")
                page.screenshot(path=screenshot_path)
                break
    
    def _find_show_more_button(self, page):
        """
        Ищет кнопку "Показать еще" различными способами
        
        Args:
            page: Объект страницы Playwright
            
        Returns:
            str: Селектор кнопки или None, если кнопка не найдена
        """
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
    
    def _scroll_and_find_button(self, page):
        """
        Прокручивает страницу и ищет кнопку "Показать еще"
        
        Args:
            page: Объект страницы Playwright
            
        Returns:
            str: Селектор кнопки или None, если кнопка не найдена
        """
        # Сначала ищем без прокрутки
        button = self._find_show_more_button(page)
        if button:
            return button
        
        # Если не нашли, прокручиваем и ищем
        logger.info("Прокручиваем страницу для поиска кнопки...")
        
        # Прокручиваем до конца страницы
        page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1000)")
        
        return self._find_show_more_button(page)
    
    def _highlight_all_buttons(self, page):
        """
        Подсвечивает все кнопки на странице для отладки
        
        Args:
            page: Объект страницы Playwright
        """
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
        screenshot_path = os.path.join(self.output_dir, "highlighted_buttons.png")
        page.screenshot(path=screenshot_path)