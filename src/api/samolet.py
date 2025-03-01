import os
import sys

# Добавляем путь к корневой папке проекта, чтобы импортировать модули из других папок
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.file_utils import generate_csv_filename
from src.utils.logging import logger

from tqdm import tqdm

import requests
import csv

from time import sleep
from random import randint

logger.info("Fetching data from Samolet API")

filename = generate_csv_filename("samolet")
logger.info(f"Saving data to {filename}")

# URL для запросов
base_url = "https://samolet.ru/backend/api_redesign/flats/"

params = {
    "nameType": "sale",
    "free": 1,
    "type": 100000000,
    "ordering": "-order_manual,filter_price_package,pk",
    "limit": 12
}

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru",
    "baggage": "sentry-environment=PROD,sentry-release=master,sentry-public_key=6f0fe185684eda71da9741fe58c43591,sentry-trace_id=785a1578ba544dfbaec5744552a607fe,sentry-sample_rate=0.1,sentry-transaction=flats,sentry-sampled=true",
    "Cookie": "sessionid=m234fo7po0qdoi3wtiyi6z53b00gjsiy; pageviewCount=1; pageviewCountMSK=1; csrftoken=QEyx80qUIAAiQE4x0oTos44UaxGkmzvRQWSuHUpALIukOV6sDhfX6Yl986AlK2sy; call_s=___htlowve6.1740841959.827160772.185717:571622|2___; _ct=1300000000511022996; _ct_client_global_id=300f34dc-3657-551a-b875-e36bcdc8ffc2; _ct_ids=htlowve6%3A36409%3A827160772; _ct_session_id=827160772; _ct_site_id=36409; qrator_jsid=1740840151.800.xH4N6kY4hrvP03i0-kvu4o51pjn9seqdhsgudcfcoh0tiu6o1; qrator_ssid=1740840152.624.u2zGc0273SgTtqsp-rml160lbq2lvl8iarrmu9dne2mqst1pn; qrator_jsr=1740840151.800.xH4N6kY4hrvP03i0-6lc14ga38mic8800qhic2aoh521kf7ha-00; popmechanic_sbjs_migrations=popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; directCrm-session=%7B%22deviceGuid%22%3A%22b49257e2-6d54-4e2e-ab1e-f97d3bb2cb52%22%7D; mindboxDeviceUUID=b49257e2-6d54-4e2e-ab1e-f97d3bb2cb52; _smt=f9bcd40e-4ab0-4c58-bd15-248676447ae1; suggested_city=1",
    "Priority": "u=3, i",
    "Referer": "https://samolet.ru/flats/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sentry-trace": "785a1578ba544dfbaec5744552a607fe-b5e4c982ee95cfa1-1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
}

flats_count = 10000

selected_fields = ["project", "floor_number", "total_floors", "living_area", "area", "price", "rooms", "is_apartment", "penthouse", "metro_set.name", "metro_set", "settling_date_formatted"]

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(selected_fields)

    for offset in tqdm(range(0, flats_count, 12)):
        logger.info(f"Fetching data for offset {offset}")

        params["offset"] = offset
        params["page"] = offset // 12 + 1

        response = requests.get(base_url, params=params, headers=headers)

        logger.debug(f"Response status code: {response.status_code} for offset {offset}")

        if response.status_code == 200:
            data = response.json()
            print(len(data.get("results", [])))
            for flat in data.get("results", []):
                row = []

                for field in selected_fields:
                    row.append(flat.get(field, ""))

                writer.writerow(row)
            
            logger.info(f"Fetched data for offset {offset}")
        else:
            logger.error(f"Failed to fetch data for offset {offset}: {response.status_code}")
        

        logger.debug(f"Waiting before next request")

        sleep(randint(1, 3)) # Ждем случайное количество секунд перед следующим запросом




