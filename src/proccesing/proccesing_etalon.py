import numpy as np
import pandas as pd

df = pd.read_csv('etalon_2025-03-02.csv', header='infer', sep=',')

df1 = df[['rooms','area', 'price', 'price_per_meter',
       'completion_date','detail_Проект', 'detail_Метро',
       'detail_Адрес', 'detail_Корпус','detail_Этаж']]


df1['metro_public_transport_time'] = np.nan
df1['district'] = np.nan
df1['district_population'] = np.nan
df1['district_avg_salary'] = np.nan

df1 = df1.rename(columns={'detail_Проект': 'complex'})
new_df = pd.merge(df1, data, on='complex', how='inner')

new_df = new_df.rename(columns={'detail_Корпус':'building','completion_date':'check_in',
                        'detail_Этаж':'floor','detail_Метро':'metro','detail_Адрес':'adress'})

new_df['developer'] = 'etalon'
new_df.to_csv('final_etalon.csv', index=False)