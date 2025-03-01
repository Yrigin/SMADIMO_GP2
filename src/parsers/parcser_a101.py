import requests
import pandas as pd

def get_flats_data(limit, offset):
    url = f"https://a101.ru/api/v2/flat/?ordering=actual_price&view=card&filter_type=price&limit={limit}&offset={offset}&city=msk&ab_test=false"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None

def main():
    flats_list = []
    limit = 100  
    total_flats = 6044 

    for offset in range(0, total_flats, limit):
        flats_data = get_flats_data(limit, offset)
        if flats_data:
            for flat in flats_data.get('results', []):
                flat_info = {
                    "ID": flat.get('id'),
                    "Article": flat.get('article'),
                    "Status": flat.get('status'),
                    "Complex": flat.get('complex'),
                    "Building": flat.get('building'),
                    "Building Number": flat.get('building_number'),
                    "Stage": flat.get('stage'),
                    "Section Number": flat.get('section_number'),
                    "Floor": flat.get('floor'),
                    "Max Floor": flat.get('max_floor'),
                    "Room": flat.get('room'),
                    "Room Name": flat.get('room_name'),
                    "Area": flat.get('area'),
                    "Price": flat.get('price'),
                    "Actual Price": flat.get('actual_price'),
                    "PPM": flat.get('ppm'),
                    "Actual PPM": flat.get('actual_ppm'),
                    "Sale Value": flat.get('sale_value'),
                    "Small Layout": flat.get('small_layout'),
                    "Big Layout": flat.get('big_layout'),
                    "Redesign Layout 1": flat.get('redevelopment_layout_1'),
                    "Redesign Layout 2": flat.get('redevelopment_layout_2'),
                    "Redesign Layout 3": flat.get('redevelopment_layout_3'),
                    "Design Layout": flat.get('design_layout'),
                    "Is Two Floor Flat": flat.get('is_two_floor_flat'),
                    "Number on Floor": flat.get('number_on_floor'),
                    "Ignore Update": flat.get('ignore_update'),
                    "First Name": flat.get('first_name'),
                    "Patronymic Name": flat.get('patronymic_name'),
                    "Last Name": flat.get('last_name'),
                    "Master Bedroom": flat.get('master_bedroom'),
                    "Two Bathrooms": flat.get('two_bathrooms'),
                    "Two Windows Room": flat.get('two_windows_room'),
                    "Bathroom Window": flat.get('bathroom_window'),
                    "Storage Dressing Room": flat.get('storage_dressing_room'),
                    "Terrace": flat.get('terrace'),
                    "Show Certificate for Furniture or Appliances": flat.get('show_certificate_for_furniture_or_appliances'),
                    "High Flat": flat.get('hightflat'),
                    "Increased Ceiling Height": flat.get('increased_ceiling_height'),
                    "Studio": flat.get('studio'),
                    "Euro": flat.get('euro'),
                    "Room Type": flat.get('room_type'),
                    "View Apartment": flat.get('view_apartment'),
                    "Smart Flat": flat.get('smart_flat'),
                    "RSHB": flat.get('rshb'),
                    "Start Sales": flat.get('start_sales'),
                    "Has Parking": flat.get('has_parking'),
                    "Has Underground Car Place": flat.get('has_underground_car_place'),
                    "Has Underground Storage": flat.get('has_underground_storage'),
                    "Metro": flat.get('metro'),
                    "Metro Time": flat.get('metro_time'),
                    "Metro Color": flat.get('metro_color'),
                    "Payment": flat.get('payment'),
                    "Min Rate": flat.get('min_rate'),
                    "Deposit": flat.get('deposit'),
                    "Mortgage Type": flat.get('mortgage_type'),
                    "Mortgage Spec Sber": flat.get('mortgage_spec_sber'),
                    "Interiors Price": flat.get('interiors_price'),
                    "Mindbox Offer ID": flat.get('mindbox_offer_id'),
                    "View Apartment Water": flat.get('view_apartment_water'),
                    "View Apartment Forest Park": flat.get('view_apartment_forest_park'),
                    "View Apartment Boulevard": flat.get('view_apartment_boulevard'),
                    "View Apartment Courtyard": flat.get('view_apartment_courtyard'),
                    "Floor Genplan": flat.get('floor_genplan'),
                    "Floor Genplan Webp": flat.get('floor_genplan_webp')
                }
                flats_list.append(flat_info)

    df = pd.DataFrame(flats_list)
    df.to_csv('flats_data.csv', index=False)
    print("Данные успешно сохранены в flats_data.csv")

if __name__ == "__main__":
    main()


df = pd.read_csv('flats_data.csv', header='infer', sep=',')

def get_complex_data():
    url = "https://a101.ru/api/v2/updated_complex/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None

def main():
    complex_list = []
    complex_data = get_complex_data()

    if complex_data:
        for complex in complex_data:
            complex_info = {
                "ID": complex.get('id'),
                "Is Active": complex.get('is_active'),
                "Settlement Slug": complex.get('settlement_slug'),
                "Realized": complex.get('realized'),
                "Has Infra": complex.get('has_infra'),
                "Has Parking": complex.get('has_parking'),
                "Start Sales": complex.get('start_sales'),
                "Title": complex.get('title'),
                "Subtitle": complex.get('subtitle'),
                "Latitude": complex.get('latitude'),
                "Longitude": complex.get('longitude'),
                "Category": complex.get('category'),

                "Distance to MKAD": complex.get('distance_to_mkad'),
                "Metro Set": complex.get('metro_set'),

                "On Sale Soon": complex.get('on_sale_soon'),
                "Map Polygon Points": complex.get('map_polygon_points'),


            }
            complex_list.append(complex_info)


    df = pd.DataFrame(complex_list)
    df.to_csv('complex_data.csv', index=False)
    print("Данные успешно сохранены в complex_data.csv")

if __name__ == "__main__":
    main()

df1 = pd.read_csv('complex_data.csv', header='infer', sep=',')

df1_selected = df1[['Title', 'Latitude', 'Longitude', 'Distance to MKAD', 'Metro Set', 'Map Polygon Points']]
df1_selected = df1_selected.rename(columns={'Title': 'Complex'})
merged_df = pd.merge(df, df1_selected, on='Complex', how='inner')

df2 = pd.read_csv('a101_projectssss.csv', header='infer', sep=';')

df2 = df2.rename(columns={'Название ЖК': 'Complex'})
merged_df1 = pd.merge(merged_df, df2, on='Complex', how='inner')
merged_df1.to_csv('a101_data.csv', index=False)