import random
import time
import logging
from playwright.sync_api import Page

logger = logging.getLogger("StealthyParser")

def random_delay(min_seconds=1, max_seconds=5):
    """Создает случайную задержку между действиями"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def simulate_human_behavior(page: Page):
    """Имитирует поведение реального пользователя"""
    logger.info("🧠 Имитация человеческого поведения...")
    
    # Случайные движения мыши
    for _ in range(random.randint(3, 7)):
        x = random.randint(100, 1500)
        y = random.randint(100, 700)
        page.mouse.move(x, y, steps=random.randint(5, 10))  # Плавное движение мыши
        random_delay(0.1, 0.5)
    
    # Случайные прокрутки с разной скоростью
    scroll_amount = random.randint(300, 700)
    logger.debug(f"Прокрутка вниз на {scroll_amount}px")
    page.mouse.wheel(0, scroll_amount)
    random_delay(0.1, 0.5)
    
    # С вероятностью 40% прокручиваем немного вверх, как будто что-то заинтересовало
    if random.random() < 0.4:
        back_scroll = random.randint(100, 300)
        logger.debug(f"Прокрутка вверх на {back_scroll}px")
        page.mouse.wheel(0, -back_scroll)
        random_delay(0.1, 0.5)
    
    # Иногда выделяем текст (с вероятностью 20%)
    if random.random() < 0.2:
        text_elements = page.query_selector_all("p, h1, h2, h3, span, a")
        if text_elements:
            element = random.choice(text_elements)
            try:
                element.click(click_count=random.choice([1, 3]))  # Одиночный или тройной клик
                random_delay(0.1, 0.5)
                page.keyboard.press("Escape")  # Снимаем выделение
            except:
                pass  # Игнорируем ошибки при клике
    
    # Иногда "думаем" дольше (с вероятностью 30%)
    if random.random() < 0.3:
        random_delay(0.1, 0.5)
    
    # Имитация изучения контента
    page.mouse.wheel(0, random.randint(100, 400))
    random_delay(0.1, 0.5)