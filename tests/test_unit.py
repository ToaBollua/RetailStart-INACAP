import pytest
from fastapi.testclient import TestClient
import sys, os, time

# Añadir el path de srv-api-backend para importar main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../servicios/srv-api-backend')))
from main import app, buffer

client = TestClient(app)

def test_ingest_endpoint(capsys):
    print("\n[H0P3-TEST] INICIANDO VALIDACIÓN UNITARIA DE INGESTA (API BACKEND)")
    print("[H0P3-TEST] Purgando buffer residual de la memoria...")
    buffer.clear()
    
    tx_id = f"TX-UNIT-{int(time.time())}"
    payload = {
        "id": tx_id,
        "data": {
            "sku": "SKU-MON-4K",
            "canal": "web",
            "cliente": "CLI-001",
            "precio": 349990,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "nodo": "test-runner"
        }
    }
    
    print(f"[H0P3-TEST] Simulando transmisión desde Dashboard Cliente. Payload ID: {tx_id}")
    response = client.post("/ingest", json=payload)
    
    print(f"[H0P3-TEST] Respuesta del servidor recibida. Status HTTP: {response.status_code}")
    assert response.status_code == 200
    
    json_resp = response.json()
    print(f"[H0P3-TEST] Analizando respuesta JSON: {json_resp}")
    assert json_resp["status"] == "ok"
    assert json_resp["buffer_size"] == 1
    
    print(f"[H0P3-TEST] Verificando inserción en el buffer en memoria de FastAPI...")
    assert len(buffer) == 1
    assert buffer[0]["id"] == tx_id
    print("[H0P3-TEST] [EXITO] Endpoint POST /ingest validado correctamente.\n")

def test_get_buffer_endpoint(capsys):
    print("\n[H0P3-TEST] INICIANDO VALIDACIÓN UNITARIA DE LECTURA (ELT POLLING)")
    print("[H0P3-TEST] Simulando escaneo del worker ELT sobre el endpoint GET /buffer...")
    
    response = client.get("/buffer")
    print(f"[H0P3-TEST] Respuesta del servidor recibida. Status HTTP: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json().get("data", [])
    print(f"[H0P3-TEST] Lote extraído: {len(data)} registros encolados.")
    assert len(data) == 1
    assert data[0]["data"]["sku"] == "SKU-MON-4K"
    
    print("[H0P3-TEST] Verificando que el buffer se vació tras la lectura (comportamiento de cola)...")
    assert len(buffer) == 0
    print("[H0P3-TEST] [EXITO] Endpoint GET /buffer validado correctamente.\n")
