import os
import requests
from functools import lru_cache

token = "35899797b14983a7193debbfeb4832620cebc332"

@lru_cache(maxsize=10000000)
def get_air_quality(lat: float, lon: float) -> dict:
    """
    Получает данные о качестве воздуха по заданным координатам.

    Параметры:
        lat (float): Широта
        lon (float): Долгота

    Возвращает:
        dict: Словарь с данными о качестве воздуха или сообщение об ошибке.

    """

    print(f"get_air_quality: {lat}, {lon}")
    if not token:
        raise ValueError("WAQI_TOKEN не найден в переменных окружения")

    # Формирование URL запроса
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверка на HTTP ошибки
        data = response.json()

        # Обработка ошибок API
        if data.get("status") != "ok":
            return {"error": data.get("message", "Неизвестная ошибка API")}

        # Извлечение основных данных
        aqi = data["data"]["aqi"]
        iaqi = data["data"]["iaqi"]
        dominant = data["data"]["dominentpol"]

        # Форматирование результата
        result = {
            "aqi": aqi,
            "dominant_pollutant": dominant,
            "pm25": iaqi.get("pm25", {}).get("v", "Нет данных"),
            "pm10": iaqi.get("pm10", {}).get("v", "Нет данных"),
            "o3": iaqi.get("o3", {}).get("v", "Нет данных"),
            "no2": iaqi.get("no2", {}).get("v", "Нет данных"),
            "so2": iaqi.get("so2", {}).get("v", "Нет данных"),
            "co": iaqi.get("co", {}).get("v", "Нет данных"),
            "temperature": iaqi.get("t", {}).get("v", "Нет данных"),
            "humidity": iaqi.get("h", {}).get("v", "Нет данных"),
            "aqi_category": _get_aqi_category(aqi),
        }
        # print(result)

        return result

    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка запроса: {str(e)}"}
    except KeyError as e:
        return {"error": f"Некорректный формат ответа API: {str(e)}"}

def _get_aqi_category(aqi: int) -> str:
    """Возвращает текстовое описание уровня загрязнения."""
    if aqi <= 50:
        return "Хороший"
    elif aqi <= 100:
        return "Умеренный"
    elif aqi <= 150:
        return "Нездоровый для чувствительных групп"
    elif aqi <= 200:
        return "Нездоровый"
    elif aqi <= 300:
        return "Очень нездоровый"
    else:
        return "Опасный"

# Пример использования
if __name__ == "__main__":
    # Установите WAQI_TOKEN в переменные окружения перед запуском
    air_quality = get_air_quality(55.7558, 37.6176)  # Координаты Москвы
    print(air_quality)