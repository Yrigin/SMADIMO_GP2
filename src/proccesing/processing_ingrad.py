import pandas as pd
import numpy as np
#обработка ingrad_flats.xlsx
df = pd.read_excel('ingrad_flats.xlsx')

columns = [
    "ID", "Пустой", "rooms", "complex", "building", "number_flat", 
    "floor", "area", "check_in", "Пустой2", "price"
]

df.columns = columns

df = df.drop(columns=["ID", "Пустой", "Пустой2"])


#обработка ingrad_description-02-03-2025.csv
df_projects = pd.read_excel('ingrad_description-02-03-2025.csv')

columns_projects = [
    "link", "complex", "description"
]
df_projects.columns = columns_projects


# мердж данных 
final_ingrad = pd.merge(df, df_projects, on='complex', how='left')

#Update 

df_pik = pd.read_excel('df_pik-02-03-2025.xlsx')
df_ingrad = pd.read_excel('final_ingrad.xlsx')
df_ingrad_description = pd.read_csv('ingrad_2025-03-03.csv')

df_pik = df_pik.drop(columns=["Unnamed: 0","flat_link","project_link"])

df_pik['developer'] = "Пик"

df_pik['metro_walk_time'] = pd.NA
df_pik['metro_car_time'] = pd.NA
df_pik['metro_public_transport_time'] = pd.NA
df_pik['district'] =pd.NA
df_pik['district_population'] = pd.NA
df_pik['district_avg_salary'] = pd.NA
df_pik['distance_to_mkad'] = pd.NA
df_pik['lag'] = pd.NA
df_pik['log'] = pd.NA

df_pik['area'] = df_pik['area'].str.replace(' ', '', regex=False)  # Убираем пробелы
df_pik['area'] = df_pik['area'].str.replace('м²', '', regex=False)  # Убираем "м²"
df_pik['area'] = pd.to_numeric(df_pik['area'], errors='coerce')

df_pik['price'] = df_pik['price'].str.replace(' ', '', regex=False)  # Убираем пробелы
df_pik['price'] = df_pik['price'].str.replace('₽', '', regex=False)  # Убираем "₽"
df_pik['price'] = pd.to_numeric(df_pik['price'], errors='coerce')

df_pik['price_per_metre'] = df_pik['price'] / df_pik['area']

df_pik['price_per_metre'] = df_pik['price_per_metre'].round(0).astype(pd.Int64Dtype())

df_ingrad = df_ingrad.drop(columns=["Unnamed: 0","link"])

df_ingrad['developer'] = "Инград"

df_ingrad['metro_walk_time'] = pd.NA
df_ingrad['metro_car_time'] = pd.NA
df_ingrad['metro_public_transport_time'] = pd.NA
df_ingrad['district'] =pd.NA
df_ingrad['district_population'] = pd.NA
df_ingrad['district_avg_salary'] = pd.NA
df_ingrad['distance_to_mkad'] = pd.NA
df_ingrad['lag'] = pd.NA
df_ingrad['log'] = pd.NA

df_ingrad['price'] = df_ingrad['price'].str.replace(' ', '', regex=False)  # Убираем пробелы
df_ingrad['price'] = df_ingrad['price'].str.replace('₽', '', regex=False)  # Убираем "₽"
df_ingrad['price'] = pd.to_numeric(df_ingrad['price'], errors='coerce')

df_ingrad['area'] = df_ingrad['area'].str.replace(' ', '', regex=False)  # Убираем пробелы
df_ingrad['area'] = df_ingrad['area'].str.replace('м²', '', regex=False)  # Убираем "м²"
df_ingrad['area'] = pd.to_numeric(df_ingrad['area'], errors='coerce')

df_ingrad['price_per_metre'] = df_ingrad['price'] / df_ingrad['area']


df_ingrad['price_per_metre'] = df_ingrad['price'] / df_ingrad['area']
df_ingrad['price_per_metre'] = df_ingrad['price_per_metre'].round(0).astype(pd.Int64Dtype())

df_ingrad_description = df_ingrad_description.drop(columns=["Unnamed: 0","Ссылка"])

df_ingrad_description = df_ingrad_description.rename(columns={
    'Заголовок': 'complex',
    'Описание': 'description',
    'Информация о метро': 'metro_distance'
})
df_ingrad_description= df_ingrad_description.drop(columns=["description"])

df_ingrad_final = pd.merge(df_ingrad,df_ingrad_description, on='complex', how='left' )
df_ingrad_final= df_ingrad_final.drop(columns=["number_flat"])


df_ingrad_final_naming = {
    "ж/д станция Мытищи - 6,5 км, ж/д станция Тайнинская - 6 км, ж/д станция Перловская - 7,8 км":"Мытищи",
    "ж/д станция Заветы Ильича - 1,5 км, ж/д станция Пушкино - 2,3 км": "Пушкино",
    "м. Домодедовская - 5 км, м. Зябликово - 5,5 км": "Домодедовская",
    "м. Саларьево - 3 км\nНа машине или на автобусе № 298 от остановки «ЖК Филатов Луг», м. Филатов Луг - 2,6 км": "Филатов Луг",
    "ж/д станция Мытищи - 3,5 км, м. Медведково - 8 км": "Мытищи",
    "МЦК Балтийская - 200 м, ст. м. Войковская - 1 км": "Балтийская",
    "м. Нагорная - 100 м, м. Нагатинская - 1 км\n.": "Нагорная",
    "м. Автозаводская - 1,3 км, МЦК «Автозаводская» - 2,07 км": "Автозаводская",
    "м. Автозаводская - 700 м": "Автозаводская",
    "ж/д станция «Отрадное» - 2 км, м. Молодежная - 18 км": "Отрадное"
    
}


df_ingrad_final_naming_dis = {
    "ж/д станция Мытищи - 6,5 км, ж/д станция Тайнинская - 6 км, ж/д станция Перловская - 7,8 км":"6,5 км",
    "ж/д станция Заветы Ильича - 1,5 км, ж/д станция Пушкино - 2,3 км": "2,3 км",
    "м. Домодедовская - 5 км, м. Зябликово - 5,5 км": "5 км",
    "м. Саларьево - 3 км\nНа машине или на автобусе № 298 от остановки «ЖК Филатов Луг», м. Филатов Луг - 2,6 км": "2,6 км",
    "ж/д станция Мытищи - 3,5 км, м. Медведково - 8 км": "3,5 км",
    "МЦК Балтийская - 200 м, ст. м. Войковская - 1 км": "200 м",
    "м. Нагорная - 100 м, м. Нагатинская - 1 км\n.": "100 м",
    "м. Автозаводская - 1,3 км, МЦК «Автозаводская» - 2,07 км": " 1,3 км",
    "м. Автозаводская - 700 м": "700 м",
    "ж/д станция «Отрадное» - 2 км, м. Молодежная - 18 км": "2 км"
    
}

df_ingrad_final['metro'] = df_ingrad_final['metro_distance'].apply(lambda x: df_ingrad_final_naming.get(x, np.nan))

df_ingrad_final['metro_distance'] = df_ingrad_final['metro_distance'].apply(lambda x: df_ingrad_final_naming_dis.get(x, np.nan))

df_pik['metro_distance'] = np.nan 


df_union = pd.concat([df_pik, df_ingrad_final], ignore_index=True)

df_union.to_excel('df_ingrad_pik_final.xlsx')
