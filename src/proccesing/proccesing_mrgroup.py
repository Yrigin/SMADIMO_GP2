import pandas as pd
import ast


projects = {
    "МИRA": "Москва, Проспект Мира, 186а",
    "SET": "Москва, ул. Верейская",
    "Павелецкая Сити": "Москва, Дубининская улица, 59Б",
    "VEER": "Москва, ул. Багрицкого",
    "Cityzen": "Москва, улица Тушинская, 24, стр. 17",
    "JOIS": "Москва, 3-й Силикатный проезд, владение 10",
    "Метрополия": "Москва, Волгоградский проспект, 32",
    "Селигер Сити": "Москва, Ильменский проезд, 14",
    "Symphony 34": "Москва, 2-я Хуторская улица, 34",
    "Mod": "Москва, 4-я улица Марьиной Рощи, 12",
    "SLAVA": "Москва, Ленинградский проспект, 8",
    "City Bay": "Москва, Волоколамское шоссе, 95-97",
    "У реки. Эко Видное 2.0": "Московская область, Ленинский район, город Видное, рядом с деревней Ермолино",
    "Famous": "Багратионовский пр., 5, Москва",
    "Noble": "Багратионовский пр., 5, Москва",
    "Nicole": "Москва, ул. Никольская",
    "LUCE": "Крестовоздвиженский пер., 4, Москва"
}



# Чтение данных из CSV файла
df = pd.read_csv('/Users/petr/hse/SMADIMO_GP2/data/mrgroup_2025-03-01.csv')

# Функция для извлечения данных из строки JSON
def extract_json_data(json_str, key):
    try:
        data = ast.literal_eval(json_str)
        return data.get(key, None)
    except (ValueError, SyntaxError):
        return None

# Создание нового DataFrame с нужными полями
new_df = pd.DataFrame()

new_df['area'] = df['area']
new_df['floor'] = df['floor']
new_df['rooms_number'] = df['rooms_number']
new_df['complex'] = df['project'].apply(lambda x: extract_json_data(x, 'name'))
new_df['description_complex'] = df['project'].apply(lambda x: extract_json_data(x, 'description'))
new_df['developer'] = 'MR Group'  # Предполагаем, что застройщик один для всех записей
new_df['address'] = new_df['complex'].apply(lambda x: projects[x])


new_df.to_csv("final_mrgroup.csv")