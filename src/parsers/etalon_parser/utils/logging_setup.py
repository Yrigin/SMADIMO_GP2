import logging
import sys
from datetime import datetime

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

def setup_logger(name="StealthyParser", log_file="extraction.log"):
    """Настройка логирования с цветным выводом в консоль и записью в файл"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Проверяем, есть ли уже обработчики
    if not logger.handlers:
        # Обработчик для вывода в файл
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Обработчик для вывода в консоль с цветами
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
    
    return logger

def log_start(logger):
    """Логирует начало парсинга с разделителем"""
    logger.info("=" * 60)
    logger.info(f"🥷 НАЧАЛО СКРЫТОГО ПАРСИНГА: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)