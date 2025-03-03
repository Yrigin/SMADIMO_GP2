import pandas as pd
import re
import ast
import json
from tqdm import tqdm

def process_dataframe(input_file, output_file):
    """
    Обрабатывает данные квартир согласно требованиям:
    1. Убирает столбцы error и presentation_url
    2. Распаковывает details по отдельным колонкам
    3. Пересчитывает area как сумму площадей комнат
    4. Выделяет скидку в отдельный столбец
    
    Args:
        input_file: Путь к исходному CSV-файлу
        output_file: Путь для сохранения обработанного CSV-файла
    """
    print(f"Загрузка данных из {input_file}...")
    
    # Пробуем загрузить данные с разными кодировками
    try:
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1251']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                print(f"Успешно загружено с кодировкой: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("Не удалось определить кодировку файла")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None
    
    print(f"Загружено {len(df)} записей")
    
    # 1. Удаляем столбцы error и presentation_url
    if 'error' in df.columns:
        df = df.drop(columns=['error'])
        print("Удален столбец 'error'")
    
    if 'presentation_url' in df.columns:
        df = df.drop(columns=['presentation_url'])
        print("Удален столбец 'presentation_url'")
    
    # Создаем новый DataFrame для обработанных данных
    processed_data = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Обработка строк"):
        processed_row = {}
        
        # Копируем базовые поля
        for field in df.columns:
            if field not in ['error', 'presentation_url', 'details', 'room_sizes']:
                processed_row[field] = row[field]
        
        # 2. Распаковываем details по отдельным колонкам
        try:
            if pd.notna(row.get('details')) and row.get('details'):
                details_str = str(row['details'])
                
                # Пытаемся преобразовать строку в словарь
                try:
                    # Метод 1: использование ast.literal_eval
                    details = ast.literal_eval(details_str)
                except (SyntaxError, ValueError):
                    # Метод 2: регулярные выражения для извлечения пар ключ-значение
                    details = {}
                    matches = re.findall(r"'([^']+)':\s*'([^']+)'", details_str)
                    for key, value in matches:
                        details[key] = value
                
                # Добавляем каждый ключ из details как отдельное поле
                for key, value in details.items():
                    processed_row[f'detail_{key}'] = value
        except Exception as e:
            print(f"Ошибка при обработке details для URL {row.get('url', 'unknown')}: {e}")
        
        # 3. Пересчитываем area как сумму площадей комнат
        try:
            if pd.notna(row.get('room_sizes')) and row.get('room_sizes'):
                room_sizes_str = str(row['room_sizes'])
                
                # Пытаемся преобразовать строку в словарь
                try:
                    # Метод 1: использование ast.literal_eval
                    room_sizes = ast.literal_eval(room_sizes_str)
                except (SyntaxError, ValueError):
                    # Метод 2: регулярные выражения для извлечения пар комната-размер
                    room_sizes = {}
                    matches = re.findall(r"'([^']+)':\s*'([^']+)'", room_sizes_str)
                    for room, size in matches:
                        room_sizes[room] = size
                
                # Добавляем каждый ключ из room_sizes как отдельное поле
                for room, size in room_sizes.items():
                    processed_row[f'room_size_{room}'] = size
                
                # Пересчитываем общую площадь как сумму площадей комнат
                total_area = 0
                for room, size in room_sizes.items():
                    try:
                        # Преобразуем строку в число, обрабатывая как точки, так и запятые
                        size_value = float(size.replace(',', '.'))
                        total_area += size_value
                    except (ValueError, TypeError):
                        print(f"Не удалось преобразовать площадь '{size}' для комнаты '{room}' в число")
                
                if total_area > 0:
                    processed_row['calculated_area'] = round(total_area, 1)
                    processed_row['original_area'] = row.get('area')  # Сохраняем оригинальное значение
        except Exception as e:
            print(f"Ошибка при обработке room_sizes для URL {row.get('url', 'unknown')}: {e}")
        
        # 4. Выделяем скидку в отдельный столбец
        try:
            completion_date = str(row.get('completion_date', ''))
            discount_match = re.search(r'(-\d+%)', completion_date)
            
            if discount_match:
                discount = discount_match.group(1)
                processed_row['discount'] = discount
                
                # Обновляем completion_date, удаляя информацию о скидке
                clean_completion_date = completion_date.replace(discount, '').strip()
                if clean_completion_date:
                    processed_row['completion_date'] = clean_completion_date
            
        except Exception as e:
            print(f"Ошибка при обработке скидки для URL {row.get('url', 'unknown')}: {e}")
        
        # Добавляем обработанную строку в новый набор данных
        processed_data.append(processed_row)
    
    # Создаем новый DataFrame из обработанных данных
    processed_df = pd.DataFrame(processed_data)
    
    # Заполняем пустые значения
    processed_df = processed_df.fillna('')
    
    # Сохраняем результат
    print(f"Сохранение результатов в {output_file}...")
    processed_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Готово! Обработано {len(df)} строк, создано {len(processed_df.columns)} столбцов.")
    print(f"Новые столбцы: {', '.join(processed_df.columns)}")
    
    return processed_df

# Пример использования
if __name__ == "__main__":
    input_file = "results.csv"  # Путь к исходному файлу
    output_file = "results_processed.csv"  # Путь для сохранения результата
    
    processed_df = process_dataframe(input_file, output_file)
    
    if processed_df is not None:
        # Выводим статистику по новым данным
        print("\nСтатистика по данным:")
        print(f"Всего квартир: {len(processed_df)}")
        
        # Статистика по комнатам
        if 'rooms' in processed_df.columns:
            # Преобразуем в числовой формат для корректной сортировки
            processed_df['rooms_numeric'] = pd.to_numeric(processed_df['rooms'], errors='coerce')
            room_counts = processed_df['rooms_numeric'].value_counts().sort_index().to_dict()
            print("\nРаспределение по количеству комнат:")
            for room, count in room_counts.items():
                if pd.notna(room):
                    print(f"  {int(room)}-комнатных: {count}")
        
        # Статистика по ценам
        if 'price' in processed_df.columns:
            price_numeric = pd.to_numeric(processed_df['price'], errors='coerce')
            valid_prices = price_numeric.dropna()
            if not valid_prices.empty:
                print("\nСтатистика по ценам (руб):")
                print(f"  Минимальная: {valid_prices.min():,.0f}")
                print(f"  Средняя: {valid_prices.mean():,.0f}")
                print(f"  Максимальная: {valid_prices.max():,.0f}")
        
        # Статистика по площади
        if 'calculated_area' in processed_df.columns:
            area_numeric = pd.to_numeric(processed_df['calculated_area'], errors='coerce')
            valid_areas = area_numeric.dropna()
            if not valid_areas.empty:
                print("\nСтатистика по расчетной площади (м²):")
                print(f"  Минимальная: {valid_areas.min():.1f}")
                print(f"  Средняя: {valid_areas.mean():.1f}")
                print(f"  Максимальная: {valid_areas.max():.1f}")
        
        # Статистика по скидкам
        if 'discount' in processed_df.columns:
            discount_count = processed_df['discount'].replace('', pd.NA).dropna().count()
            if discount_count > 0:
                print(f"\nКвартир со скидкой: {discount_count} ({discount_count/len(processed_df)*100:.1f}%)")
                
                # Попытка вычислить среднюю скидку
                try:
                    discount_values = []
                    for discount in processed_df['discount']:
                        if discount:
                            match = re.search(r'-(\d+)%', discount)
                            if match:
                                discount_values.append(int(match.group(1)))
                    
                    if discount_values:
                        avg_discount = sum(discount_values) / len(discount_values)
                        print(f"Средняя скидка: {avg_discount:.1f}%")
                except Exception as e:
                    print(f"Ошибка при анализе скидок: {e}")
        
        # Статистика по проектам
        project_col = 'detail_Проект'
        if project_col in processed_df.columns:
            project_counts = processed_df[project_col].replace('', pd.NA).dropna().value_counts().to_dict()
            print("\nРаспределение по проектам:")
            for project, count in sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {project}: {count}")