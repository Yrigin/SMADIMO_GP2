import pandas as pd
import ast

projects = {
    "Событие": "ул. Лобачевского, 114, Москва, 119361",
    "Символ": "Москва, улица Крузенштерна, 2",
    "Остров": "ул. Нижние Мнёвники, 37А строение 2, Москва, 123423"
}

# Чтение данных из CSV файла
df = pd.read_csv('/Users/petr/hse/SMADIMO_GP2/data/donstroi_2025-03-01.csv')

# Создание нового DataFrame с нужными полями
new_df = pd.DataFrame()

new_df['price'] = df['Price'].apply(lambda x: int(x.replace(' ₽', '').replace(',', '').replace(' ', '')))
new_df['area'] = df['Square'].apply(lambda x: float(x.replace(' м²', '').replace(',', '.')))
new_df['floor'] = None  # Предполагаем, что данных о этаже нет
new_df['rooms_number'] = df['Title'].apply(lambda x: 0 if 'Cтудия' in x else int(x.split('-')[0][0]))
new_df['complex'] = df['Address']

new_df['developer'] = 'Donstroi'  # Предполагаем, что застройщик один для всех записей
new_df['address'] = new_df['complex'].apply(lambda x: projects.get(x, 'Неизвестно'))


# Сохранение результата в новый CSV файл
new_df.to_csv('/Users/petr/hse/SMADIMO_GP2/data/final_donstroi.csv', index=False)
