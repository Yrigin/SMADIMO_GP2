import requests
from typing import Dict, Optional, List
from functools import lru_cache
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSRM_URL = "http://router.project-osrm.org/route/v1"

@lru_cache(maxsize=100000000)
def calculate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    mode: str = 'walking'
) -> Optional[Dict[str, float]]:
    
    """
    Расчет маршрута между двумя точками.
    :param mode: Режим (driving, walking, cycling)
    :return: Словарь с расстоянием (км) и временем (мин)
    """
    print(f"calculate_route: {start_lat}, {start_lon}, {end_lat}, {end_lon}")
    try:
        response = requests.get(
            f"{OSRM_URL}/{mode}/{start_lon},{start_lat};{end_lon},{end_lat}",
            timeout=10
        )
        response.raise_for_status()
        route = response.json().get('routes', [{}])[0]
        return {
            'distance_km': route.get('distance', 0) / 1000,  # Переводим метры в километры
            'time_min': route.get('duration', 0) / 60  # Переводим секунды в минуты
        }
    except (requests.exceptions.RequestException, KeyError, IndexError):
        return None
    
@lru_cache(maxsize=100000000)
def get_nearest_metro_mcd(lat: float, lon: float, radius_km: int = 3) -> Optional[Dict]:
    """
    Возвращает ближайшую станцию метро/МЦД, расстояние до неё и время в пути (пешком).
    :param lat: Широта
    :param lon: Долгота
    :param radius_km: Радиус поиска в километрах
    :return: Словарь с названием станции, типом, координатами, расстоянием и временем в пути
    """
    print(f"get_nearest_metro_mcd: {lat}, {lon}")
    radius = radius_km * 1000  # Переводим километры в метры
    query = f"""
    [out:json];
    (
      node["railway"="station"]["station"="subway"](around:{radius},{lat},{lon});
      node["railway"="station"]["station"="light_rail"](around:{radius},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    try:
        # Запрашиваем станции метро/МЦД
        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers={'Content-Type': 'text/plain'},
            timeout=20
        )
        response.raise_for_status()
        stations = response.json().get('elements', [])

        if not stations:
            return None

        # Находим ближайшую станцию
        nearest_station = None
        min_distance = float('inf')

        for station in stations:
            station_lat = station.get('lat')
            station_lon = station.get('lon')
            if station_lat is None or station_lon is None:
                continue

            # Рассчитываем расстояние до станции
            route = calculate_route(lat, lon, station_lat, station_lon, mode='walking')
            if route and route['distance_km'] < min_distance:
                min_distance = route['distance_km']

                
                nearest_station = {
                    'name': station.get('tags', {}).get('name', None),
                    'type': "metro" if station.get('tags', {}).get('station') == "subway" else "mcd",
                    'coordinates': (station_lat, station_lon),
                    'distance_km': route['distance_km'],
                    'time_min': route['time_min']
                }

        return nearest_station

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    
@lru_cache(maxsize=100000000)
def count_infrastructure(
    lat: float,
    lon: float,
    radius_km: int,
    infrastructure_types: List[str] = None
) -> Dict[str, int]:
    """
    Подсчет объектов инфраструктуры через Overpass API.
    :param lat: Широта
    :param lon: Долгота
    :param radius_km: Радиус поиска в километрах
    :param infrastructure_types: Список тегов OSM (school, hospital и т.д.)
    :return: Словарь с количеством объектов каждого типа
    """
    print(f"count_infrastructure: {lat}, {lon}")
    if infrastructure_types is None:
        infrastructure_types = [
            'school', 'kindergarten', 'hospital', 'pharmacy',
            'park', 'supermarket', 'cafe', 'restaurant'
        ]

    radius = radius_km * 1000  # Переводим километры в метры
    counts = {}

    for infra_type in infrastructure_types:
        query = f"""
        [out:json];
        node["amenity"="{infra_type}"](around:{radius},{lat},{lon});
        out count;
        """
        try:
            response = requests.post(
                OVERPASS_URL,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=20
            )
            data = response.json()
            counts[infra_type] = data['elements'][0]['tags'].get('total', 0)
        except Exception:
            counts[infra_type] = 0

    return counts


import requests
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

# Координаты центра Москвы (примерно центр МКАД)
MOSCOW_CENTER = (55.7558, 37.6176)
    
@lru_cache(maxsize=100000000)
def get_mkad_boundary() -> Optional[dict]:
    """
    Загружает границы МКАД из Overpass API.
    :return: Геометрия МКАД в формате GeoJSON
    """
    query = """
    [out:json];
    relation["name"="Московская кольцевая автомобильная дорога"]["type"="route"];
    out geom;
    """
    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers={'Content-Type': 'text/plain'},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        if data.get('elements'):
            return data['elements'][0]['geometry']
        return None
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")
    
@lru_cache(maxsize=100000000)
def calculate_distance_to_mkad(lat: float, lon: float) -> Optional[float]:
    """
    Рассчитывает расстояние от заданных координат до МКАД.
    :param lat: Широта
    :param lon: Долгота
    :return: Расстояние в километрах
    """
    # Загружаем границы МКАД
    mkad_geometry = get_mkad_boundary()
    if not mkad_geometry:
        return None

    # Преобразуем границы МКАД в объект Shapely
    mkad_line = shape({
        "type": "LineString",
        "coordinates": [[node['lon'], node['lat']] for node in mkad_geometry]
    })

    # Создаем точку из заданных координат
    point = Point(lon, lat)

    # Находим ближайшую точку на МКАД
    nearest_point = nearest_points(point, mkad_line)[1]

    # Рассчитываем расстояние в метрах и переводим в километры
    distance_km = point.distance(nearest_point) / 1000
    return distance_km


if __name__ == "__main__":
    # Тестовые координаты (Кремль)
    lat, lon = 55.752004, 37.617734

    # 1. Ближайшее метро/МЦД
    print("Ближайшая станция метро/МЦД:")
    print(get_nearest_metro_mcd(lat, lon, radius_km=2))

    # 2. Инфраструктура
    print("\nКоличество объектов инфраструктуры:")
    print(count_infrastructure(lat, lon, 1))