import pandas as pd
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

