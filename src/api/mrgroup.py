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

logger.info("Fetching data from MRGROUP API")

filename = generate_csv_filename("mrgroup")
logger.info(f"Saving data to {filename}")

# URL для запросов
base_url = "https://www.mr-group.ru/api/sale/products"

params = {
    "category": "flats",
    "page": 1,
    "limit": 48
}

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru",
    "baggage": "sentry-environment=production,sentry-public_key=64d42d1ec99f4044ff0df570a905dbca,sentry-trace_id=21f08ea6dd234e59b73c58a2bf1a843c,sentry-sample_rate=0.1,sentry-transaction=%2Fflats%2F*,sentry-sampled=false",
    "Cookie": "PHPSESSID=gepbejavd0q7cbqri5o04505sj; PHPSESSID=c4g20pm5uquusl5c9736eo4326; USE_COOKIE_CONSENT_STATE={%22session%22:true%2C%22persistent%22:true%2C%22necessary%22:true%2C%22preferences%22:true%2C%22statistics%22:true%2C%22marketing%22:true%2C%22firstParty%22:true%2C%22thirdParty%22:true}; spsc=1740845039807_4c1f1924bb06cc3f0fe7217ce2dc5c47_e6cfb3ea8f0a0fa28cc6ebefdcae8ea5; spid=1740595988307_48ca1a1a51c16507a855e6f57ab27234_chdd2o56wdgak714",
    "Priority": "u=3, i",
    "Referer": "https://www.mr-group.ru/flats/page-2/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sentry-trace": "21f08ea6dd234e59b73c58a2bf1a843c-b1617efa6ad646f1-0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
}

flats_count = 3723
pages = int(flats_count / 48)


selected_fields = ["name",
                    "price",
                    "area",
                    "floor",
                    "rooms_number",
                    "project",
                    "meter_price" ]

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(selected_fields)

    for offset in tqdm(range(0, pages)):
        logger.info(f"Fetching data for page {offset}")

        params["page"] = offset

        response = requests.get(base_url, params=params, headers=headers)

        logger.debug(f"Response status code: {response.status_code} for page {offset}")

        if response.status_code == 200:
            data = response.json()
            
            for flat in data.get("items", []):
                row = []

                for field in selected_fields:
                    row.append(flat.get(field, ""))

                writer.writerow(row)
            
            logger.info(f"Fetched data for page {offset}")
        else:
            logger.error(f"Failed to fetch data for page {offset}: {response.status_code}")
        

        logger.debug(f"Waiting before next request")

        sleep(randint(1, 2)) # Ждем случайное количество секунд перед следующим запросом




