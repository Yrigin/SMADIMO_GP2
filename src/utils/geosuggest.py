import requests
from functools import lru_cache
API_KEY = "0fb89937-645f-4951-9e21-1e146c4ec163"
from pprint import pprint
@lru_cache(maxsize=10000000)
def cord_to_address(lon, lat):
    print(f"cord_to_address: {lon}, {lat}")
    url = f"https://geocode-maps.yandex.ru/1.x?geocode={lon},{lat}&format=json&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        object = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']
        return {
            "name": object['name'],
            "address": object['metaDataProperty']['GeocoderMetaData']['text']
        }
        return response.json()
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None
    
@lru_cache(maxsize=10000000)
def address_to_cord(address):
    print(f"address_to_cord: {address}")
    url = f"https://geocode-maps.yandex.ru/1.x?geocode={address}&format=json&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        object = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']
        return {
            "lon": object['Point']['pos'].split()[0],
            "lat": object['Point']['pos'].split()[1]
        }
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None
@lru_cache(maxsize=10000000)
def get_metro(lon, lat):
    url = f"https://geocode-maps.yandex.ru/1.x?geocode={lon},{lat}&kind=metro&format=json&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        object = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']
        return {
            "name": object['name']
        }
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None
    
@lru_cache(maxsize=10000000)
def get_district(lon, lat):
    url = f"https://geocode-maps.yandex.ru/1.x?geocode={lon},{lat}&kind=district&format=json&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        objects = response.json()["response"]["GeoObjectCollection"]["featureMember"]
        pprint(objects)
        obj_names = [object['GeoObject']['name'] for object in objects]
        for obj_name in obj_names:
            if 'район' in obj_name:
                return {
                    "name": obj_name
                }
        return {
            "name": obj_names[0]['GeoObject']['name']
        }
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None
    
@lru_cache(maxsize=10000000)
def get_location_by_coords(lon, lat):
    print(f"get_location_by_coords: {lon}, {lat}")
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": API_KEY,
        "geocode": f"{lon},{lat}",
        "format": "json",
        "kind":"district"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Ошибка запроса: {response.status_code}")

    data = response.json()
    
    try:
        components = (data["response"]["GeoObjectCollection"]
                          ["featureMember"][0]["GeoObject"]
                          ["metaDataProperty"]["GeocoderMetaData"]
                          ["Address"]["Components"])
        
        subject = None
        city = None
        district = None  # Новая переменная для района

        for component in components:
            pprint(component)
            kind = component["kind"]
            if kind == "province":
                subject = component["name"]
            elif kind == "locality":
                city = component["name"]
            elif kind == "district":  # Захватываем район города
                district = component["name"]

        if subject not in ["Москва", "Московская область"]:
            return None, None, None  # Обновлено на три значения

        return subject, city, district  # Возвращаем район

    except (KeyError, IndexError):
        return None, None, None  # Три None при ошибке
    


    print(f"get_location_by_coords: {lon}, {lat}")
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": API_KEY,
        "geocode": f"{lon},{lat}",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Ошибка запроса: {response.status_code}")

    data = response.json()
    
    try:
        components = (data["response"]["GeoObjectCollection"]
                          ["featureMember"][0]["GeoObject"]
                          ["metaDataProperty"]["GeocoderMetaData"]
                          ["Address"]["Components"])
        
        subject = None
        city = None

        for component in components:
            print(component)
            if component["kind"] == "province":
                subject = component["name"]
            elif component["kind"] == "locality":
                city = component["name"]

        if subject not in ["Москва", "Московская область"]:
            return None, None  # Фильтруем только нужные регионы

        return subject, city

    except (KeyError, IndexError):
        return None, None
    
if __name__ == '__main__':
    # address = input("Введите адрес: ")
    # print(get_metros(address))
    cords = address_to_cord('г. Одинцово, ул. Комсомольская, д. 1')
    print(cords)
    # print(get_district(37.65115, 55.715441))
    # print(get_location_by_coords(37.65115, 55.715441))
    print(get_location_by_coords(37.571076, 55.80611))



    # print(get_metro(**cords))
    # print(cord_to_address('37.632763', '55.697894'))
    # print(get_metro('37.632763', '55.697894'))
    # print(get_district('37.632763', '55.697894'))