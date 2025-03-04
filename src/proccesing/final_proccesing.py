import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.geosuggest import cord_to_address, address_to_cord, get_location_by_coords
from src.utils.air_quality import get_air_quality
from src.utils.infastructure import get_nearest_metro_mcd, count_infrastructure, calculate_distance_to_mkad
from utils.district import get_district
df = pd.read_csv("./finaldf2.csv")
from time import sleep



import math

def distance_from_moscow_center(lat, lon):
    # Координаты центра Москвы (Кремль)
    moscow_lat = 55.751244
    moscow_lon = 37.618423
    
    # Радиус Земли в километрах
    earth_radius = 6371.0
    
    # Преобразование градусов в радианы
    lat1_rad = math.radians(moscow_lat)
    lon1_rad = math.radians(moscow_lon)
    lat2_rad = math.radians(lat)
    lon2_rad = math.radians(lon)
    
    # Разница координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Формула гаверсинусов
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c
    
    return distance  # Возвращает расстояние в километрах
df["lat"] = df.apply(lambda row: address_to_cord(row['address'])["lat"] if pd.isnull(row["lat"]) and pd.notnull(row["address"]) else row["lat"], axis=1)
df["lon"] = df.apply(lambda row: address_to_cord(row['address'])["lon"] if pd.isnull(row["lon"]) and pd.notnull(row["address"]) else row["lon"], axis=1)

# Fill missing address using lat/lon
df["address"] = df.apply(lambda row: cord_to_address(row["lon"], row["lat"]) if pd.isnull(row["address"]) and pd.notnull(row["lat"]) and pd.notnull(row["lon"]) else row["address"], axis=1)


df["geosubject"] = df[["lat", "lon"]].apply(lambda x: get_location_by_coords(x[1], x[0])[0], axis=1)
df["geocity"] = df[["lat", "lon"]].apply(lambda x: get_location_by_coords(x[1], x[0])[1], axis=1)
df["geoprovince"] = df[["lat", "lon"]].apply(lambda x: get_location_by_coords(x[1], x[0])[2], axis=1)

df["air_quality"] = df[["lat", "lon"]].apply(lambda x: get_air_quality(x[0], x[1])["aqi_category"], axis=1)
df["humidity"] = df[["lat", "lon"]].apply(lambda x: get_air_quality(x[0], x[1])["humidity"], axis=1)

# ## Добавляем столбцы с информацией о ближайшей станции метро/МЦД
def nearest_metro_mcd_info(lat, lon):
    try:
        station_info = get_nearest_metro_mcd(lat, lon)
        if station_info:
            print(station_info)
            return pd.Series([station_info['name'], station_info['type'], station_info['coordinates'][0], station_info['coordinates'][1], station_info['distance_km'], station_info['time_min']])
        else:
            return pd.Series([None, None, None, None, None, None])
    except:
        print("eeror")
        sleep(10)
        return pd.Series([None, None, None, None, None, None])


infrastructure_types = ['school', 'kindergarten', 'hospital', 'pharmacy', 'park', 'supermarket', 'cafe', 'restaurant']
for infra_type in infrastructure_types:
    df[f"{infra_type}_count"] = df[["lat", "lon"]].apply(lambda x: count_infrastructure(x[0], x[1], 2).get(infra_type, 0), axis=1)

df['distance_from_msc_centre'] = df[["lat", "lon"]].apply(lambda x: distance_from_moscow_center(x[0], x[1]), axis=1)
df[['nearest_metro_name', 'nearest_metro_type', 'nearest_metro_lat', 'nearest_metro_lon', 'nearest_metro_distance_km', 'nearest_metro_time_min']] = df[["lat", "lon"]].apply(lambda x: nearest_metro_mcd_info(x[0], x[1]), axis=1)

df.drop(columns=['Unnamed: 0'], inplace=True)
df.to_csv("data/final/final_df.csv")