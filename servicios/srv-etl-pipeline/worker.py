import os, time, logging, json, signal, sys
from pymongo import MongoClient
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ETL")

MONGO_HOST = os.getenv("MONGO_HOST", "srv-db-mongo-primary")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASS = os.getenv("MONGO_PASS", "rootpass")
PG_URI = os.getenv("PG_URI")

running = True

def handle_sigterm(sig, frame):
    global running
    logger.info("SIGTERM recibido. Cerrando ETL worker.")
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
    pg_engine = create_engine(PG_URI)

    with pg_engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_events (
                id VARCHAR(255) PRIMARY KEY,
                data JSONB,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
    logger.info("Tabla fact_events verificada en Postgres.")

    while running:
        try:
            mongo = get_mongo_db()
            records = list(mongo.raw_events.find({"processed": {"$ne": True}}).limit(100))
            if records:
                with pg_engine.begin() as conn:
                    for r in records:
                        conn.execute(
                            text("INSERT INTO fact_events (id, data) VALUES (:id, :data) ON CONFLICT DO NOTHING"),
                            {"id": r["id"], "data": json.dumps(r["data"])}
                        )
                        mongo.raw_events.update_one({"_id": r["_id"]}, {"$set": {"processed": True}})
                logger.info(f"Transformados {len(records)} registros hacia Postgres.")
        except Exception as e:
            logger.error(f"Error de ETL: {e}")
        time.sleep(10)

if __name__ == "__main__":
    run()
