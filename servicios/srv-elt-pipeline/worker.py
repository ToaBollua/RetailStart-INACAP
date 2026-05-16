import os, time, requests, logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ELT")

MONGO_URI = os.getenv("MONGO_URI")
API_URL = os.getenv("API_URL")

def run():
    client = MongoClient(MONGO_URI)
    db = client.retail_lake
    while True:
        try:
            res = requests.get(f"{API_URL}/buffer")
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    db.raw_events.insert_many(data)
                    logger.info(f"Escritos {len(data)} registros en Mongo.")
        except Exception as e:
            logger.error(f"Falla en lectura: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run()
