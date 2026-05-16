from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

app = FastAPI(title="Retail API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")

buffer = []

class Payload(BaseModel):
    id: str
    data: dict

@app.post("/ingest")
async def ingest_data(payload: Payload):
    buffer.append(payload.model_dump())
    logger.info(f"Ingested: {payload.id}")
    return {"status": "ok", "buffer_size": len(buffer)}

@app.get("/buffer")
async def get_buffer():
    # Volcando buffer.
    data = list(buffer)
    buffer.clear()
    return {"data": data}
