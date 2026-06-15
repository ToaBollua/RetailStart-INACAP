import time
import requests
import random
import json
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("RETAIL-SIMULATOR")

API_URL = "http://localhost:8000"

CLIENTES = [
    "Empresas Falabella", "Cencosud Holding", "Sodimac Constructor", 
    "WalMart Chile", "Ripley S.A.", "TecnoChile Ltda", "Logistica Sur",
    "Juan Perez S.A.", "Maria Gomez E.I.R.L.", "Distribuidora Santiago"
]

PRODUCTOS = [
    {"nombre": "Notebook Pro 15", "precio_base": 850000},
    {"nombre": "Monitor UltraWide 34", "precio_base": 349990},
    {"nombre": "Teclado Mecanico RGB", "precio_base": 59990},
    {"nombre": "Mouse Gamer Inalambrico", "precio_base": 45000},
    {"nombre": "Silla Ergonomica", "precio_base": 129990},
    {"nombre": "Auriculares Cancelacion Ruido", "precio_base": 189990},
    {"nombre": "Servidor Rack 1U", "precio_base": 2500000},
    {"nombre": "Disco Duro SSD 2TB", "precio_base": 120000}
]

CANALES = ["web", "tienda_fisica", "app_movil"]

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def simulate():
    logger.info("[SIM] Generando datos de transacciones simuladas...")
    
    # 1. Enviar transacciones a través de la API
    total_txs = 150
    enviados = []
    
    for i in range(total_txs):
        tx_id = f"TX-SIM-{100000 + i}"
        cliente = random.choice(CLIENTES)
        prod = random.choice(PRODUCTOS)
        # Variar el precio un poco (descuentos o variaciones menores)
        precio = int(prod["precio_base"] * random.uniform(0.9, 1.1))
        canal = random.choice(CANALES)
        
        payload = {
            "id": tx_id,
            "data": {
                "cliente": cliente,
                "producto": prod["nombre"],
                "precio": precio,
                "canal": canal
            }
        }
        
        try:
            res = requests.post(f"{API_URL}/ingest", json=payload, timeout=2)
            if res.status_code == 200:
                enviados.append(tx_id)
        except Exception as e:
            logger.error(f"Error al enviar transacción {tx_id}: {e}")
            break
            
    logger.info(f"[SIM] Se enviaron exitosamente {len(enviados)} transacciones al API.")
    
    # 2. Esperar a que el pipeline procese todo
    logger.info("[SIM] Esperando 12 segundos a que el worker ELT mueva los datos a Mongo...")
    time.sleep(12)
    logger.info("[SIM] Esperando 15 segundos a que el worker ETL transforme y mueva los datos a Postgres...")
    time.sleep(15)
    
    # 3. Validar cuántos registros llegaron
    pg_count_query = "SELECT COUNT(*) FROM fact_events;"
    pg_cmd = f'docker exec -e PGPASSWORD=retail_pass srv-db-postgres-primary psql -U retail_user -d retail_dw -t -c "{pg_count_query}"'
    stdout, stderr, rcode = run_command(pg_cmd)
    
    if rcode == 0:
        logger.info(f"[SIM] Registros totales en Postgres fact_events: {stdout.strip()}")
    else:
        logger.error(f"[SIM] Error al consultar Postgres: {stderr}")
        return
    
    # 4. Actualizar fechas en Postgres de forma aleatoria en el pasado
    # Distribuiremos las transacciones en los últimos 7 días (168 horas)
    logger.info("[SIM] Distribuyendo transacciones temporalmente en los últimos 7 días...")
    
    # Obtener todas las claves primarias (ids)
    pg_ids_query = "SELECT id FROM fact_events WHERE id LIKE 'TX-SIM-%';"
    pg_ids_cmd = f'docker exec -e PGPASSWORD=retail_pass srv-db-postgres-primary psql -U retail_user -d retail_dw -t -c "{pg_ids_query}"'
    stdout, stderr, rcode = run_command(pg_ids_cmd)
    
    if rcode == 0:
        ids = [line.strip() for line in stdout.split('\n') if line.strip()]
        logger.info(f"[SIM] Encontrados {len(ids)} registros de simulación en Postgres para actualizar.")
        
        # Ejecutar actualizaciones individuales o en lotes para simular fechas
        for idx, tx_id in enumerate(ids):
            # Restar entre 1 y 168 horas (7 días) de forma aleatoria
            hours_offset = random.randint(1, 168)
            # Query para restar horas a processed_at
            update_query = f"UPDATE fact_events SET processed_at = NOW() - INTERVAL '{hours_offset} hours' WHERE id = '{tx_id}';"
            update_cmd = f'docker exec -e PGPASSWORD=retail_pass srv-db-postgres-primary psql -U retail_user -d retail_dw -t -c "{update_query}"'
            _, _, r_code = run_command(update_cmd)
            if r_code != 0:
                logger.error(f"[SIM] Error actualizando {tx_id}")
                
        logger.info("[SIM] Actualización de timestamps finalizada con éxito. Simulación cronológica lista.")
    else:
        logger.error(f"[SIM] Error al listar ids: {stderr}")

if __name__ == "__main__":
    simulate()
