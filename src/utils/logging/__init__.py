import logging
import sys
from pathlib import Path

# Настройки логгера
LOG_FILE = Path("app.log")  # Путь к файлу логов
LOG_FORMAT = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"  # Формат сообщений
LOG_LEVEL = logging.INFO  # Уровень логирования

def setup_logger():
    # Создаем логгер
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)

    # Проверяем, нет ли уже обработчиков (чтобы избежать дублирования)
    if not logger.handlers:
        # Создаем форматтер
        formatter = logging.Formatter(LOG_FORMAT)

        # Обработчик для записи в файл
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Обработчик для вывода в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Инициализируем логгер
logger = setup_logger()