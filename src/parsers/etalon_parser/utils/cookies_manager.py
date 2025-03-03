import json
import os
import logging

logger = logging.getLogger("StealthyParser")

def load_cookies(context, cookies_file='etalon_cookies.json'):
    """Загружает cookies из файла, если он существует"""
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

def save_cookies(context, cookies_file='etalon_cookies.json'):
    """Сохраняет cookies в файл для последующего использования"""
    cookies = context.cookies()
    with open(cookies_file, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False)
    logger.info(f"🍪 Сохранено {len(cookies)} cookies в файл")