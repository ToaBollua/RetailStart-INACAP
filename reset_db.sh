#!/bin/bash
# H0P3 Epsilon DB Reset Utility v3.0

echo "[*] INICIANDO RESET COMPLETO DE BASES DE DATOS (RETAILSMART)"
echo "============================================================"

# 1. Reset MongoDB NoSQL Lake
echo "[*] Purgando base de datos NoSQL MongoDB (retail_lake)..."
docker exec srv-db-mongo-primary mongosh -u root -p rootpass --eval "use retail_lake; db.dropDatabase();" --quiet
echo "[+] MongoDB limpio con éxito."

# 2. Reset y Semilla en PostgreSQL DW
echo "[*] Ejecutando pipeline incremental de 10 días para PostgreSQL..."
.venv/bin/python3 run_pipeline.py

echo "============================================================"
echo "[+] RESET Y POBLACIÓN DE 10 DÍAS COMPLETADA EXITOSAMENTE!"
