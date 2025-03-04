import pandas as pd
import os

def combine_files(directory):

    mr = pd.read_csv(directory + '/final_mrgroup.csv')
    a101 = pd.read_csv(directory + '/final_a101.csv')
    # inpik = pd.read_csv(directory + '/final_df_ingrad_pik.csv')
    inpik = pd.read_excel(directory + '/final_df_ingrad_pik.xlsx')
    donstroi = pd.read_csv(directory + '/final_donstroi.csv')
    etalon = pd.read_csv(directory + '/final_etalon.csv')
    sreda = pd.read_csv(directory + '/final_sreda.csv')
    etalon.rename(columns={"adress": "address"}, inplace=True)

    a101.rename(columns={"price_per_metre": "price_per_meter"}, inplace=True)
    inpik.rename(columns={"price_per_metre": "price_per_meter"}, inplace=True)
    sreda.rename(columns={"price_per_metre": "price_per_meter"}, inplace=True)

    a101.rename(columns={"description": "description_complex"}, inplace=True)
    inpik.rename(columns={"description": "description_complex"}, inplace=True)
    etalon.rename(columns={"description": "description_complex"}, inplace=True)
    sreda.rename(columns={"description": "description_complex"}, inplace=True)


    mr.rename(columns={"rooms_number": "rooms"}, inplace=True)
    donstroi.rename(columns={"rooms_number": "rooms"}, inplace=True)
    sreda.rename(columns={"rooms_number": "rooms"}, inplace=True)
    
    inpik["floor"] = inpik["floor"].apply(lambda x: x.replace("Этаж", "").split('из')[0])
    inpik["rooms"] = inpik["rooms"].apply(lambda x: x if x in ["Пентхаус", "Таунхаус"] else x.split()[0])
    inpik["rooms"] = inpik["rooms"].apply(lambda x: 0 if "Студия" in x else x)

    etalon["floor"] = inpik["floor"].apply(lambda x: x.replace("Этаж", "").split('из')[0])
    etalon["rooms"] = inpik["floor"].apply(lambda x: x.replace(".0", ""))

    sreda["floor"] = sreda["floor"].apply(lambda x: x.replace("Этаж", "").split('/')[0])
    sreda["price"] = sreda["price"].apply(lambda x: x.replace(" ", "").replace("₽", "")).astype(int)
    sreda["area"] = sreda["area"].apply(lambda x: x.replace("м2", "").replace(" ", "")).astype(float)
    # sreda["rooms"] = sreda["rooms"].apply(lambda x: x.split('/')[0])
    # sreda.drop(columns=''], inplace=True)
    # inpik["rooms"] = inpik["rooms"].apply(lambda x: x if "a" not in x else x.split('a')[0])
    # for item in [mr, a101, inpik, donstroi, etalon, sreda]:
    #     # item.drop(columns=['Unnamed: 0', "metro", "distance_to_mkad", "metro_car_time", "metro_walk_time", "metro_distance", 'metro_public_transport_time', "district", "district_population", "district_avg_salary"], inplace=True)
    #     print("=====================================")
    #     print(item.developer.value_counts())
    #     print(item.columns)
    #     # print(item.shape)
    #     # print(item.floor.value_counts())
    #     print(item.rooms.value_counts())
    #     # print(item.area.value_counts)
    #     # print(item.price.value_counts)
    #     print("=====================================")

    df = pd.concat([mr, a101, inpik, donstroi, etalon,sreda], ignore_index=True)
    return df

# Example usage
directory = 'data/final'
df = combine_files(directory)

df.drop(columns=['Unnamed: 0', "metro", "distance_to_mkad", "metro_car_time", "metro_walk_time", "metro_distance", 'metro_public_transport_time', "district", "district_population", "district_avg_salary"], inplace=True)
df["price_per_meter"] = df['price']/df['area']
df.rename(columns={"log": "lon"}, inplace=True)
df.rename(columns={"lag": "lat"}, inplace=True)
print("=====================================")
# print(df.head())
print(df.columns)

df.to_csv('data/final/final_data.csv', index=True)