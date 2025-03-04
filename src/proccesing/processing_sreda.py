# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# Обработка sreda.xlsx
df = pd.read_csv('/Users/strel/Documents/SMADIMO_GP2/data/sreda_2025_03_02.csv')

columns = ['complex', 'building', 'address', 'check_in', 'floor', 'rooms', 'area', 'price', 'price_per_metre', 'lag', 'log', 'distance_to_mkad',
    'description', 'metro', 'metro_car_time', 'metro_walk_time', 'metro_distance', 'developer', 'metro_public_transport_time',
    'district', 'district_population', 'district_avg_salary']

sreda_columns = ['developer', 'complex', 'metro_name', 'metro_walk_time', 'apartment_type', 'area', 'price', 'price for м2', 'Корпус', 'floor',
    'rooms_number', 'Отделка', 'Срок сдачи']

# Переименовываем столбцы
df = df.rename(columns={
    'metro_name': 'metro',
    'Срок сдачи': 'check_in',
    'price for м2': 'price_per_metre',
    'Корпус': 'building'
})

# Удаляем лишние столбцы
df = df[[col for col in df.columns if col in columns]]

# Добавляем недостающие столбцы и заполняем их NaN
for col in columns:
    if col not in df.columns:
        df[col] = np.nan

# Указываем тип данных для столбца 'description' как строковый, чтобы не выдавал ошибку
df['description'] = df['description'].astype('string')

print(df.columns)

complex = df['complex'].unique()
print(complex)

df.loc[df['complex'] == 'Среда на Лобачевского', 'lag'] = 55.691440
df.loc[df['complex'] == 'Среда на Лобачевского', 'lоg'] = 37.458804

df.loc[df['complex'] == 'Среда на Кутузовском', 'lag'] = 55.728573
df.loc[df['complex'] == 'Среда на Кутузовском', 'lоg'] = 37.432575

df.loc[df['complex'] == 'Среда на Лобачевского', 'description'] = 'Жилой комплекс бизнес-класса «Среда на Лобачевского» строится на западе Москвы — в Очаково-Матвеевском создается кластер для комфортной жизни в мегаполисе. Продуманный современный экстерьер и функциональные планировки внутри, приватные пространства и разнообразные досуговые зоны для каждого члена семьи — все это «Среда на Лобачевского».'
df.loc[df['complex'] == 'Среда на Кутузовском', 'description'] = '«Среда на Кутузовском» — место для тех, кто хочет вывести свой личный комфорт на новый уровень. Квартал бизнес-класса появится на западе Москвы в престижном, экологически чистом районе Кунцево. Проект сочетает в себе ритмичность и динамичность, которые так ценят жители современного мегаполиса, но при этом бережно вписан в окружающую среду и гармонично дополняет ее.'


df.to_csv('/Users/strel/Documents/SMADIMO_GP2/data/final_sreda.csv', index=False, encoding='utf-8-sig')