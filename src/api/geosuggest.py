import requests

API_KEY = "b45f0f9d-c0e5-48bc-b4fc-20927a31b17a"

def cord_to_address(lon, lat):
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
    

def address_to_cord(address):
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

def get_district(lon, lat):
    url = f"https://geocode-maps.yandex.ru/1.x?geocode={lon},{lat}&kind=district&format=json&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        objects = response.json()["response"]["GeoObjectCollection"]["featureMember"]
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

if __name__ == '__main__':
    # address = input("Введите адрес: ")
    # print(get_metros(address))
    cords = address_to_cord('г. Москва, ул. Пушкинская, д. 1')
    print(cords)
    print(get_district(**cords))
    print(get_metro(**cords))
    print(cord_to_address('37.632763', '55.697894'))
    # print(get_metro('37.632763', '55.697894'))
    # print(get_district('37.632763', '55.697894'))