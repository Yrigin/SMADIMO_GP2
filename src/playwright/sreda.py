import asyncio
from playwright.async_api import async_playwright
import pandas as pd

# Асинхронная функция для парсинга
async def parse_apartments():
    async with async_playwright() as p:
        # Запуск браузера
        browser = await p.chromium.launch(headless=False)  # headless=False для визуального отображения
        page = await browser.new_page()

        # Переход на сайт
        await page.goto("https://sreda.ru/flats")

        # Создаем пустой список для хранения данных
        apartments_data = []

        # Функция для нажатия кнопки "Загрузить еще"
        async def load_more():
            try:
                # Ищем кнопку "Загрузить еще"
                load_more_button = await page.query_selector(
                    "xpath=//button[contains(@class, 'PageApartments_apartments__button__338LE')]"
                )
                if load_more_button:
                    # Прокручиваем страницу до кнопки
                    await load_more_button.scroll_into_view_if_needed()
                    # Нажимаем кнопку
                    await load_more_button.click()
                    # Ждем загрузки новых данных
                    await page.wait_for_timeout(5000)  # Ожидание 5 секунд
                    return True
            except Exception as e:
                print(f"Ошибка при нажатии кнопки: {e}")
            return False

        # Нажимаем кнопку "Загрузить еще" до тех пор, пока она есть
        while await load_more():
            print("Загружено больше данных")

        # Получаем все карточки квартир на главной странице
        apartments = await page.query_selector_all(".ApartmentGridCard_apartment-grid-card__dZLSw")

        # Обрабатываем каждую квартиру по очереди
        for i, apartment in enumerate(apartments):
            try:
                # Считываем метро с главной страницы
                metro = await apartment.query_selector(".ProjectShortInfo_project-short-info__font--text__JWFLB")
                metro = await metro.inner_text() if metro else "N/A"

                walk_time = await page.query_selector(".ProjectShortInfo_project-short-info__text--dark__KoaSL .ProjectShortInfo_project-short-info__font--text__JWFLB")
                walk_time = await walk_time.inner_text() if walk_time else "N/A"

                # Получаем ссылку на страницу квартиры
                apartment_link = await apartment.query_selector("a.ApartmentGridCard_apartment-grid-card__link__qGsb1")
                apartment_url = await apartment_link.get_attribute("href") if apartment_link else None

                # Если ссылка есть, переходим на страницу квартиры
                if apartment_url:
                    # Открываем новую вкладку для страницы квартиры
                    new_page = await browser.new_page()
                    await new_page.goto(f"https://sreda.ru{apartment_url}")
                    await new_page.wait_for_timeout(3000)  # Ожидание загрузки страницы

                    # Извлекаем данные о квартире
                    try:
                        # Название проекта
                        project_name = await new_page.query_selector(".ApartmentHeadHeader_apartment-head-header__project-name__awvQx")
                        project_name = await project_name.inner_text() if project_name else "N/A"

                        # Название квартиры и площадь
                        title_element = await new_page.query_selector(".ApartmentHeadHeader_apartment-head-header__title__QGQbx")
                        title_text = await title_element.inner_text() if title_element else "N/A"

                        # Извлечение типа квартиры
                        apartment_type = title_text.split(",")[0].strip() if title_text != "N/A" else "N/A"

                        # Извлечение площади
                        area = await new_page.query_selector(".ApartmentHeadHeader_apartment-head-header__title__QGQbx .nobr")
                        area = await area.inner_text() if area else "N/A"

                        # Цена
                        price = await new_page.query_selector(".ReserveAction_reserveAction__price__TJEb6")
                        price = await price.inner_text() if price else "N/A"

                        # Цена за квадратный метр
                        price_per_m2 = await new_page.query_selector(".ReserveAction_reserveAction__meterPrice__yiDVF")
                        price_per_m2 = await price_per_m2.inner_text() if price_per_m2 else "N/A"

                        # Дополнительная информация
                        info_block = await new_page.query_selector(".ApartmentHeadInfo_apartment-head-info__list__lBQbq")
                        info_items = await info_block.query_selector_all(".ApartmentHeadInfo_apartment-head-info__list-row__sWvR_")
                        info_dict = {}
                        for item in info_items:
                            key = await item.query_selector(".ApartmentHeadInfo_apartment-head-info__list-name__Owf_r")
                            value = await item.query_selector(".ApartmentHeadInfo_apartment-head-info__list-value__Oqh4h")
                            if key and value:
                                info_dict[await key.inner_text()] = await value.inner_text()

                        # Добавляем данные в список
                        apartments_data.append({
                            "developer": "Среда",
                            "complex": project_name,
                            "metro_name": metro,
                            "metro_walk_time": walk_time,
                            "apartment_type": apartment_type,
                            "area": area,
                            "price": price,
                            "price for м2": price_per_m2,
                            "Корпус": info_dict.get("Корпус", "N/A"),
                            "floor": info_dict.get("Этаж", "N/A"),
                            "rooms_number": info_dict.get("Номер квартиры", "N/A"),
                            "Отделка": info_dict.get("Отделка", "N/A"),
                            "Срок сдачи": info_dict.get("Срок сдачи", "N/A")
                        })

                        print(f"Обработана квартира {i + 1}/{len(apartments)}")


                    except Exception as e:
                        print(f"Ошибка при извлечении данных: {e}")

                    # Закрываем вкладку с квартирой
                    await new_page.close()

            except Exception as e:
                print(f"Ошибка при обработке квартиры: {e}")

        # Закрытие браузера
        await browser.close()

        # Создаем DataFrame из списка данных
        df = pd.DataFrame(apartments_data)

        # Сохраняем данные в CSV
        df.to_csv("apartments_data_sreda.csv", index=False, encoding="utf-8-sig")

        # Сохраняем данные в Excel
        df.to_excel("apartments_data_sreda.xlsx", index=False)

        # Выводим DataFrame в консоль для проверки
        print(df)

# Запуск асинхронной функции
asyncio.run(parse_apartments())