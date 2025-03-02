# parsers/base_parser.py (обновлённая версия)

import logging
import os
import json
import pandas as pd
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, Page
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

logger = logging.getLogger("StealthyParser")

class BaseParser(ABC):
    """Базовый класс для парсеров с общей функциональностью"""
    
    def __init__(self, max_workers=None):
        """
        Инициализация базового парсера
        
        Args:
            max_workers: Максимальное количество параллельных процессов
        """
        self.max_workers = max_workers or min(cpu_count(), 4)
        self.results = []
    
    @abstractmethod
    def parse_page(self, page: Page, url: str):
        """
        Метод для парсинга отдельной страницы, должен быть реализован в подклассах
        
        Args:
            page: Объект страницы Playwright
            url: URL страницы для парсинга
            
        Returns:
            dict: Словарь с извлеченными данными
        """
        pass
    
    def load_urls(self, file_path):
        """Загружает список URL для парсинга из файла"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                urls = json.load(f)
            logger.info(f"Загружено {len(urls)} URL из {file_path}")
            return urls
        except Exception as e:
            logger.error(f"Ошибка при загрузке URL из {file_path}: {e}")
            return []
    
    def filter_processed_urls(self, urls, result_file="result.csv"):
        """Фильтрует URL, которые уже были обработаны"""
        if os.path.exists(result_file):
            # Загружаем существующие данные
            df = pd.read_csv(result_file)
            logger.info(f"Загружен существующий файл с {len(df)} записями")
            
            # Получаем список уже обработанных URL
            processed_urls = df['url'].tolist()
            
            # Отфильтровываем только необработанные URL
            urls_to_process = [url for url in urls if url not in processed_urls]
            logger.info(f"Осталось обработать {len(urls_to_process)} из {len(urls)} URL")
            
            return urls_to_process, df
        else:
            # Если файла нет, создаем пустой DataFrame и обрабатываем все URL
            logger.info(f"Файл с результатами не найден. Будут обработаны все {len(urls)} URL")
            return urls, pd.DataFrame()
    
    @staticmethod
    def process_url(url, parser_type="etalon"):
        """
        Статический метод для обработки URL в отдельном процессе
        
        Args:
            url: URL для обработки
            parser_type: Тип парсера ('etalon' или 'links')
            
        Returns:
            dict: Результат парсинга или None в случае ошибки
        """
        try:
            from utils.logging_setup import setup_logger
            from utils.browser_utils import setup_browser_context, setup_page_stealth
            
            # Настраиваем логирование в каждом процессе
            logger = setup_logger()
            
            # Создаем новый экземпляр Playwright в каждом процессе
            with sync_playwright() as p:
                # Настраиваем браузер и контекст
                browser, context = setup_browser_context(p, headless=True)
                if not browser or not context:
                    logger.error("Не удалось настроить браузер")
                    return None
                
                # Создаем новую страницу
                page = context.new_page()
                setup_page_stealth(page)
                
                # Импортируем нужный парсер в зависимости от типа
                if parser_type == "etalon":
                    from parsers.flat_parser import FlatParser
                    parser = FlatParser()
                else:  # links
                    from parsers.link_extractor_parser import LinkExtractorParser
                    parser = LinkExtractorParser(output_dir="link_extractor")
                
                # Парсим страницу
                result = parser.parse_page(page, url)
                
                # Закрываем браузер
                browser.close()
                
                return result
        except Exception as e:
            logger.error(f"Ошибка при обработке URL {url}: {str(e)}")
            return {"url": url, "error": str(e)}
    
    def run_parallel(self, urls, result_file="result.csv", existing_df=None, parser_type="etalon"):
        """
        Запускает параллельный парсинг URL в отдельных процессах
        
        Args:
            urls: Список URL для обработки
            result_file: Путь к файлу с результатами
            existing_df: Существующий DataFrame с результатами
            parser_type: Тип парсера ('etalon' или 'links')
            
        Returns:
            pd.DataFrame: DataFrame с результатами
        """
        if not urls:
            logger.info("Нет URL для обработки")
            return existing_df if existing_df is not None else pd.DataFrame()
        
        # Инициализируем DataFrame с существующими данными
        df = existing_df if existing_df is not None else pd.DataFrame()
        
        # Разбиваем URLs на батчи для периодического сохранения результатов
        batch_size = min(100, len(urls))
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        for batch_idx, batch_urls in enumerate(batches):
            logger.info(f"Обработка батча {batch_idx+1}/{len(batches)} ({len(batch_urls)} URL)")
            
            # Подготавливаем аргументы для process_url с типом парсера
            process_args = [(url, parser_type) for url in batch_urls]
            
            # Используем multiprocessing.Pool для параллельной обработки
            with Pool(processes=self.max_workers) as pool:
                # Запускаем обработку URLs с отображением прогресса
                results = list(tqdm(
                    pool.starmap(self.process_url, process_args),
                    total=len(batch_urls),
                    desc=f"Батч {batch_idx+1}/{len(batches)}"
                ))
                
                # Фильтруем успешные результаты
                valid_results = [r for r in results if r is not None]
                
                if valid_results:
                    # Добавляем новые данные к существующим
                    new_df = pd.DataFrame(valid_results)
                    df = pd.concat([df, new_df], ignore_index=True)
                    
                    # Сохраняем обновленный DataFrame после каждого батча
                    df.to_csv(result_file, index=False, encoding="utf-8-sig")
                    logger.info(f"Сохранены результаты для {len(valid_results)} URL")
        
        return df