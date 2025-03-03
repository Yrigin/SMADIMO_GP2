import logging
from playwright.sync_api import Page

logger = logging.getLogger("StealthyParser")

def parse_features_component(page: Page):
    """
    Парсит компонент "Особенности" со всеми вкладками
    Возвращает словарь с данными всех разделов
    """
    features_data = {}
    
    try:
        # Проверяем наличие компонента "Особенности" на странице
        features_title = page.query_selector("p.th-h2:has-text('Особенности')")
        
        if not features_title:
            logger.info("Компонент 'Особенности' не найден на странице")
            return features_data
        
        # Находим все вкладки
        tabs = page.query_selector_all("button.v-tab")
        
        if not tabs:
            logger.info("Вкладки в компоненте 'Особенности' не найдены")
            return features_data
        
        logger.info(f"Найдено {len(tabs)} вкладок в компоненте 'Особенности'")
        
        # Обходим все вкладки
        for i, tab in enumerate(tabs):
            try:
                # Получаем название вкладки
                tab_title_element = tab.query_selector("span.u-tab__text")
                if tab_title_element:
                    tab_title = tab_title_element.inner_text().strip()
                else:
                    tab_title = f"Вкладка {i+1}"
                
                logger.info(f"Обрабатываем вкладку: {tab_title}")
                
                # ВАЖНОЕ ИСПРАВЛЕНИЕ: Ждем, пока содержимое вкладки полностью отрендерится
                # Используем явное ожидание появления элемента в активной вкладке
                try:
                    # Ожидаем появления контейнера с содержимым в активной вкладке
                    page.wait_for_selector("div.v-window-item--active div.bg-light-gray", timeout=5000)
                    
                    # Дополнительно ждем появления заголовка в активной вкладке
                    page.wait_for_selector("div.v-window-item--active p.th-h3", timeout=5000)
                    
                    # Дополнительно ждем появления секции с текстом
                    page.wait_for_selector("div.v-window-item--active section", timeout=5000)
                    
                    # Даем дополнительное время для полного рендеринга
                    page.wait_for_timeout(500)
                except Exception as wait_error:
                    logger.warning(f"Предупреждение: Не удалось дождаться загрузки содержимого вкладки: {str(wait_error)}")
                
                # Кликаем на вкладку для активации содержимого
                tab.click()
                
                # Даем время на загрузку содержимого
                page.wait_for_timeout(1000)
                
                # Используем JavaScript для извлечения данных по точной структуре
                result = page.evaluate("""(tabName) => {
                    // Находим контейнер с особенностями по заголовку
                    const featuresSection = Array.from(document.querySelectorAll('p.th-h2'))
                        .find(el => el.textContent.trim() === 'Особенности')
                        ?.closest('div.max-w-\\\\[1210px\\\\]');
                    
                    if (!featuresSection) return { title: '', description: '', images: [] };
                    
                    // Находим активную вкладку ВНУТРИ секции особенностей
                    const activeTab = featuresSection.querySelector('.v-window-item--active');
                    if (!activeTab) return { title: '', description: '', images: [] };
                    
                    // Находим блок с информацией (div с классом bg-light-gray)
                    const infoBlock = activeTab.querySelector('div.bg-light-gray');
                    if (!infoBlock) return { title: '', description: '', images: [] };
                    
                    // Находим заголовок (p.th-h3)
                    const titleElem = infoBlock.querySelector('p.th-h3');
                    const title = titleElem ? titleElem.textContent.trim() : tabName;
                    
                    // Находим секцию с описанием, которая идет после заголовка
                    const sectionElem = infoBlock.querySelector('section');
                    
                    // Извлекаем текст из всех параграфов внутри section
                    let description = '';
                    if (sectionElem) {
                        // Собираем текст из всех параграфов, исключая контейнеры
                        const paragraphs = Array.from(sectionElem.querySelectorAll('p'))
                            .filter(p => !p.classList.contains('flex') || !p.querySelector('p'));
                        
                        const textArray = [];
                        for (const p of paragraphs) {
                            // Проверяем, является ли это непосредственным текстовым параграфом
                            if (p.childElementCount === 0 || 
                                (p.childElementCount > 0 && !p.querySelector('p'))) {
                                const text = p.textContent.trim();
                                if (text) textArray.push(text);
                            }
                        }
                        
                        description = textArray.join('\\n\\n');
                    }
                    
                    // Находим все изображения в активной вкладке
                    const images = activeTab.querySelectorAll('img.v-img__img--cover');
                    const imageUrls = Array.from(images)
                        .map(img => img.getAttribute('src'))
                        .filter(src => src);
                    
                    return {
                        title: title,
                        description: description,
                        images: imageUrls
                    };
                }""", tab_title)
                
                # Создаем словарь для данных текущей вкладки
                tab_data = result if result else {"title": tab_title, "description": "", "images": []}
                
                # Добавляем данные вкладки в общий словарь
                features_data[tab_title] = tab_data
                
                logger.debug(f"Для вкладки '{tab_title}' извлечено:")
                logger.debug(f"  - Заголовок: {tab_data.get('title', 'Не найден')}")
                desc = tab_data.get('description', 'Не найдено')
                logger.debug(f"  - Описание: {desc[:50]}..." if len(desc) > 50 else f"  - Описание: {desc}")
                logger.debug(f"  - Изображения: {len(tab_data.get('images', []))}")
            
            except Exception as e:
                logger.error(f"Ошибка при обработке вкладки {i+1}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге компонента 'Особенности': {str(e)}")
    
    return features_data