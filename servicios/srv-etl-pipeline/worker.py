import os, time, logging, json
from pymongo import MongoClient
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ETL")

MONGO_URI = os.getenv("MONGO_URI")
PG_URI = os.getenv("PG_URI")

def run():
    mongo = MongoClient(MONGO_URI).retail_lake
    pg_engine = create_engine(PG_URI)

    with pg_engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_events (
                id VARCHAR(255) PRIMARY KEY,
                data JSONB,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

    while True:
        try:
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
