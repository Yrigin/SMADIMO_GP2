import pandas as pd
import re
import numpy as np

df = pd.read_csv('/Users/sofiazimenkova/Desktop/SMADIMO_GP2/data/a101_2025-03-02.csv')
print(df.head(5))

#Выбор целевых параметров 
df = df[['Complex', 'Building Number','Stage', 'Floor', 'Max Floor', 'Room',
       'Area', 'Actual Price', 'Actual PPM','Number on Floor','Studio','Start Sales','Metro','Latitude', 'Longitude', 'Distance to MKAD', 'Metro Set','Текст']]




#форматирование Metro Set выделение 4-х отдельных переменных
def extract_metro_name(string):
    pattern = r"'title': '([^']*)'"
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    return None


def extract_metro_car_time(string):
    pattern = r"'time_on_car': ([^,}}]*)"
    match = re.search(pattern, string)
    if match:
        value = match.group(1).strip()
        if value == "None":
            return None
        try:
            return float(value)
        except ValueError:
            return value
    return None


def extract_metro_walk_time(string):
    pattern = r"'time_on_foot': ([^,}}]*)"
    match = re.search(pattern, string)
    if match:
        value = match.group(1).strip()
        if value == "None":
            return None
        try:
            return float(value)
        except ValueError:
            return value
    return None


def extract_metro_distance(string):
    pattern = r"'distance': '([^']*)'"
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    return None


df['metro_name'] = df['Metro Set'].apply(extract_metro_name)
df['metro_car_time'] = df['Metro Set'].apply(extract_metro_car_time)
df['metro_walk_time'] = df['Metro Set'].apply(extract_metro_walk_time)
df['metro_distance'] = df['Metro Set'].apply(extract_metro_distance)
df.drop(columns=['Metro Set'], inplace=True)

#добавление недостающих столбцов и переименование существующих
df['developer'] = 'a101'

df = df.rename(columns={'Complex': 'complex', 'Building Number':'building','Stage':'check_in', 
                        'Floor':'floor', 'Room':'rooms','Area':'area','Actual Price':'price',
                        'Actual PPM':'price_per_metre','Latitude':'lag','Longitude':'log','Distance to MKAD':'distance_to_mkad',
                        'Текст':'description','metro_name':'metro'})

df['metro_public_transport_time'] = np.nan
df['district'] = np.nan
df['district_population'] = np.nan
df['district_avg_salary'] = np.nan

df.to_csv('a101_2025_03_03.csv', index=False)

