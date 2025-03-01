def clean_price(price):
    # Удаляем все нечисловые символы, включая пробелы и "от"
    cleaned_price = ''.join(filter(str.isdigit, price))
    return int(cleaned_price) if cleaned_price else None  # Возвращаем None, если цена невалидна


df_pik = []
# Применяем функцию к столбцу 'price'
df_pik['price'] = df_pik['price'].apply(clean_price)

# Удаляем строки с None (если есть невалидные цены)
df_pik = df_pik.dropna(subset=['price'])

# Находим максимальное и минимальное значение
max_price = df_pik['price'].max()
min_price = df_pik['price'].min()


df_pik[['Корпус', 'Этаж']] = df_pik['Корпус/Этаж'].str.split(',', expand=True)


df_pik['Метро'] = df_pik['Метро'].str.replace('\n', '').str.strip()

split_result = df_pik['Метро'].str.split('•', n=1, expand=True)  # Разделяем по первому символу "•"
split_result.columns = ['Метро', 'ЖК']  # Переименовываем столбцы

# Заполняем пропущенные значения (если символ "•" отсутствовал)
split_result['ЖК'] = split_result['ЖК'].fillna('').str.strip()  # Заменяем NaN на пустую строку и удаляем пробелы

# Добавляем новые столбцы в DataFrame
df_pik[['Метро', 'ЖК']] = split_result




df_pik['Метро'] = df_pik['Метро'].str.strip()
df_pik['ЖК'] = df_pik['ЖК'].str.strip()
df_pik['Корпус'] = df_pik['Корпус'].str.strip()
df_pik['Этаж'] = df_pik['Этаж'].str.strip()


df_pik = df_pik.rename(columns={
    'Ссылка на объявление': 'flat_link',
    'Название': 'title',
    'Цена': 'price',
    'Метро': 'metro',
    'ЖК': 'complex',
    'Корпус': 'building',
    'Этаж': 'floor',
    'Заселение': 'check_in'
})


df_pik[['rooms', 'area']] = df_pik['title'].str.split(',', expand=True)


del df_pik['title']
