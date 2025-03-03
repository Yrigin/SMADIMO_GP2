import argparse
import logging
import os
from playwright.sync_api import sync_playwright

from utils.logging_setup import setup_logger, log_start
from utils.browser_utils import setup_browser_context, setup_page_stealth
from utils.cookies_manager import load_cookies, save_cookies
from utils.human_behavior import random_delay
from parsers.flat_parser import FlatParser
from parsers.link_extractor_parser import LinkExtractorParser

def parse_args():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(description="Скрытый парсер сайтов недвижимости")
    parser.add_argument("--parser", "-p", choices=["etalon", "links"], default="etalon", 
                        help="Выбор парсера (etalon - парсинг квартир, links - извлечение ссылок)")
    parser.add_argument("--urls", "-u", default=None, 
                        help="Путь к файлу с URL для парсинга (для etalon)")
    parser.add_argument("--output", "-o", default=None, 
                        help="Путь для сохранения результатов")
    parser.add_argument("--workers", "-w", type=int, default=4, 
                        help="Количество параллельных процессов")
    parser.add_argument("--headless", action="store_true", 
                        help="Запуск в headless режиме (без отображения браузера)")
    parser.add_argument("--method", "-m", choices=["processes", "browsers"], default="processes",
                        help="Метод параллелизации: processes - отдельные процессы, browsers - несколько браузеров")
    return parser.parse_args()

def main():
    """Основная функция программы"""
    # Парсим аргументы командной строки
    args = parse_args()
    
    # Настраиваем логирование
    logger = setup_logger()
    log_start(logger)
    
    # Определяем пути по умолчанию в зависимости от выбранного парсера
    if args.parser == "etalon":
        default_urls_path = "link_extractor/extracted_links.json"
        default_output_path = "result.csv"
    else:  # links
        default_urls_path = "https://etalongroup.ru/choose/"
        default_output_path = "link_extractor/extracted_links.json"
    
    # Устанавливаем пути по умолчанию, если они не указаны
    urls_path = args.urls if args.urls else default_urls_path
    output_path = args.output if args.output else default_output_path
    
    # Выбираем парсер на основе аргументов
    if args.parser == "etalon":
        # Создаем директорию для результатов, если она не существует
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Создана директория для результатов: {output_dir}")
            
        parser = FlatParser(max_workers=args.workers)
        
        # Загружаем URL
        urls = parser.load_urls(urls_path)
        if not urls:
            logger.error("Не удалось загрузить URL. Завершение работы.")
            return
        
        # Фильтруем уже обработанные URL
        urls_to_process, existing_df = parser.filter_processed_urls(urls, output_path)
        
        if not urls_to_process:
            logger.info("Все URL уже обработаны. Завершение работы.")
            return
        
        # Запускаем парсинг
        if args.method == "processes":
            # Используем мультипроцессинг
            results_df = parser.run_parallel(urls_to_process, output_path, existing_df)
        else:
            # Используем несколько браузеров в одном потоке
            with sync_playwright() as p:
                results_df = parser.run_parallel_browsers(urls_to_process, output_path, existing_df, not args.headless)
                
        logger.info(f"Парсинг завершен. Обработано {len(urls_to_process)} URL.")
        logger.info(f"Результаты сохранены в {output_path}")
        
    else:  # links
        # Создаем парсер для извлечения ссылок
        output_dir = os.path.dirname(output_path)
        parser = LinkExtractorParser(max_workers=args.workers, output_dir=output_dir)
        
        # Запускаем парсер для извлечения ссылок
        logger.info(f"Запускаем извлечение ссылок с {urls_path}")
        
        # Для парсера ссылок используем только один процесс, так как обрабатывается одна страница
        with sync_playwright() as p:
            # Настраиваем браузер и контекст
            browser, context = setup_browser_context(p, headless=args.headless)
            if not browser or not context:
                logger.error("Не удалось настроить браузер. Завершение работы.")
                return
            
            # Загружаем cookies если есть
            load_cookies(context)
            
            # Создаем страницу
            page = context.new_page()
            setup_page_stealth(page)
            
            # Используем случайную задержку перед началом работы
            start_delay = random_delay(0.5, 2)
            logger.debug(f"Задержка перед началом работы: {start_delay:.2f}с")
            
            # Запускаем парсинг
            parser.parse_page(page, urls_path)
            
            # Сохраняем cookies для последующего использования
            save_cookies(context)
            
            # Закрываем браузер
            browser.close()
        
        logger.info(f"Извлечение ссылок завершено. Результаты сохранены в {output_path}")

if __name__ == "__main__":
    main()