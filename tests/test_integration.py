import time
import requests
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("H0P3-TEST")

API_URL = "http://localhost:8000"

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def test_end_to_end_flow():
    test_id = f"tx-integration-{int(time.time())}"
    payload = {
        "id": test_id,
        "data": {"cliente": "Bollua_E2E", "item": "Servidor_IA", "precio": 15000}
    }

    logger.info(f"[1/4] Enviando payload de prueba al API: {test_id}")
    try:
        res = requests.post(f"{API_URL}/ingest", json=payload, timeout=5)
        assert res.status_code == 200, f"Fallo al contactar API: {res.text}"
        logger.info("API respondió OK.")
    except Exception as e:
        assert False, f"El API no está disponible en localhost:8000. ¿Está corriendo docker compose? Error: {e}"

    logger.info("[2/4] Esperando 10 segundos a que el worker ELT mueva el dato a Mongo...")
    time.sleep(10)

    logger.info("[3/4] Esperando 15 segundos a que el worker ETL transforme y mueva a Postgres...")
    time.sleep(15)

    logger.info("[4/4] Consultando directamente el Data Warehouse (Postgres)...")
    # Consultar Postgres dentro del contenedor
    sql_query = f"SELECT data FROM fact_events WHERE id = '{test_id}';"
    pg_cmd = f'docker exec -e PGPASSWORD=retail_pass srv-db-postgres-primary psql -U retail_user -d retail_dw -t -c "{sql_query}"'
    
    stdout, stderr, rcode = run_command(pg_cmd)
    
    assert rcode == 0, f"Fallo al ejecutar consulta en Postgres. Error: {stderr}"
    
    if not stdout:
        logger.error("El registro no se encontró en Postgres. Revisando logs de los pipelines...")
        elt_logs, _, _ = run_command("docker logs srv-elt-pipeline --tail 20")
        etl_logs, _, _ = run_command("docker logs srv-etl-pipeline --tail 20")
        logger.info(f"--- LOGS ELT ---\n{elt_logs}")
        logger.info(f"--- LOGS ETL ---\n{etl_logs}")
        assert False, "Prueba E2E fallida: El registro no llegó a Postgres."

    logger.info(f"Registro encontrado en Postgres: {stdout}")
    try:
        db_data = json.loads(stdout)
        assert db_data["cliente"] == "Bollua_E2E"
        logger.info("¡PRUEBA E2E COMPLETADA CON ÉXITO! Flujo de datos verificado de extremo a extremo.")
    except Exception as e:
        assert False, f"Fallo al parsear JSONB de Postgres: {stdout}. Error: {e}"

if __name__ == "__main__":
    test_end_to_end_flow()
