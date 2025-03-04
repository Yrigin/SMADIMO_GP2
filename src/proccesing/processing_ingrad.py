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



import pandas as pd
import ast


projects = {
    'Полар': '55.892435, 37.645651',
    'Белая Дача парк': '55.659568, 37.874483',
    'Кузьминский лес': '55.663132, 37.855378',
    'Восточное Бутово': '55.532501, 37.617690',
    'Люблинский парк': '55.660807, 37.731907',
    'Саларьево парк': '55.618752, 37.413034',
    'Алтуфьевское 53': '55.873821, 37.580281',
    'Барклая 6': '55.740628, 37.504147',
    'Ильинские луга': '55.775329, 37.239831',
    'Волжский парк': '55.719320, 37.725142',
    'Первый Дубровский': '55.724210, 37.682597',
    'Плеханова 11': '55.751728, 37.762296',
    'Ярославский': '55.910713, 37.784101',
    'Яуза парк': '55.912315, 37.761004',
    '2-й Иртышский': '55.814098, 37.765721',
    'Никольские луга': '55.518845, 37.572518',
    'Середневский лес': '55.567886, 37.285560',
    'Зелёный парк': '55.965120, 37.170882',
    'Бусиновский парк': '55.881298, 37.505391',
    'Кавказский бульвар 51': '55.627709, 37.640632',
    'Юнино': '55.514002, 37.574700',
    'Большая Академическая 85': '55.847014, 37.562848',
    'Матвеевский парк': '55.694138, 37.462676',
    'Кронштадтский 9': '55.842877, 37.490107',
    'Открытый парк': '55.817021, 37.757433',
    'Holland park': '55.815579, 37.427176',
    'Бутово парк 2': '55.548298, 37.587290',
    'Руставели 14': '55.812757, 37.599049',
    'Мичуринский парк': '55.669401, 37.437581',
    'Перовское 2': '55.734259, 37.739263',
    'Полярная 25': '55.882528, 37.636495',
    'Мякинино парк': '55.801961, 37.347850',
    'Кутузовский квартал': '55.728339, 37.434251',
    'Green park': '55.852964, 37.620898',
    'Кольская 8': '55.861631, 37.648250',
    'Второй Нагатинский': '55.676180, 37.640581',
    'Амурский парк': '55.805586, 37.751439',
    'Ярославский квартал': '55.910216, 37.785172',
    'Сигнальный 16': '55.852014, 37.601150',
    'Митинский лес': '55.859754, 37.375476',
    'Томилинский бульвар': '55.662804, 37.867073',
    'Ютаново': '55.587233, 37.612378',
    'Апартаменты • Большая Академическая 85': '55.845693, 37.562252',
    'Москворечье': '55.645396, 37.639925',
    'Лосиноостровский парк': '55.817201, 37.746336',
    'Красноказарменная 15': '55.756191, 37.706509',
    'Жулебино парк': '55.677589, 37.866788',
    'Римского-Корсакова 11': '55.875162, 37.596651',
    'Бунинские луга': '55.543024, 37.482866',
    'Измайловский лес': '55.784972, 37.850145',
    'Одинцово-1': '55.654824, 37.268614',
    'Большая Очаковская 2': '55.692455, 37.466557',
    'Vangarden': '55.693434, 37.459955',
    'Новое Очаково': '55.683231, 37.446252',
    'Белый Grad': '55.908077, 37.691771',
    'Новое Пушкино': '56.024564, 37.856234',
    'Миловидное': '55.593136, 37.757885',
    'Одинград': '55.678311, 37.236304',
    'Филатов луг': '55.614194, 37.385063',
    'Новое Медведково': '55.924921, 37.727118',
    'Injoy': '55.831938, 37.495438',
    'TopHills': '55.673092, 37.607372',
    'Riversky': '55.718843, 37.656179',
    'Foriver': '55.715441, 37.651150',
    'Кутузов Grad II': '55.716516, 37.429479'

}



for index, row in df_union.iterrows():
    complex_name = row['complex']
    if complex_name in projects:
        coordinates = projects[complex_name].split(', ')
        df_union.at[index, 'lag'] = float(coordinates[0])  # (lag)
        df_union.at[index, 'log'] = float(coordinates[1])  #  (log)


df_union.to_excel('final_df_ingrad_pik.xlsx')
