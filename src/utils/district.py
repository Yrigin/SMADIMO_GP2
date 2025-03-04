import geopandas as gpd
from shapely.geometry import Point
from functools import lru_cache
# Загружаем объединенный GeoJSON с районами Москвы и области
gdf = gpd.read_file("data/export.geojson")

@lru_cache(maxsize=10000000)
def get_district(lat, lon):
    """Определяет район по координатам (широта, долгота)"""
    point = Point(lon, lat)  # В GeoPandas координаты указываются как (долгота, широта)
    
    # Ищем район, содержащий точку
    for _, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return row.get('name', 'Неизвестный район')  # Поле 'name' должно содержать название района

    return None

