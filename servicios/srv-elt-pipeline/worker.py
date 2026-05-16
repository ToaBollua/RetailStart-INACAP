import os, time, requests, logging, signal, sys
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ELT")

MONGO_HOST = os.getenv("MONGO_HOST", "srv-db-mongo-primary")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASS = os.getenv("MONGO_PASS", "rootpass")
API_URL = os.getenv("API_URL")

running = True

def handle_sigterm(sig, frame):
    global running
    logger.info("SIGTERM recibido. Cerrando ELT worker.")
    running = False
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def get_mongo_db():
    """Crea una conexión directa al nodo primary, sin negociación de ReplicaSet."""
    client = MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASS,
        authSource="admin",
        directConnection=True,
        serverSelectionTimeoutMS=5000,
    )
    return client.retail_lake

def run():
    while running:
        try:
            res = requests.get(f"{API_URL}/buffer", timeout=5)
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    db = get_mongo_db()
                    db.raw_events.insert_many(data)
                    logger.info(f"Escritos {len(data)} registros en Mongo.")
        except Exception as e:
            logger.error(f"Falla en lectura: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run()
