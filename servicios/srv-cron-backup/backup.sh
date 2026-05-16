#!/bin/bash
while true; do
    TS=$(date +%Y%m%d_%H%M%S)
    echo "[CRON] Extrayendo volúmenes a /backups..."
    tar -czf /backups/mongo_${TS}.tar.gz -C /data/mongo . 2>/dev/null || true
    tar -czf /backups/postgres_${TS}.tar.gz -C /data/postgres . 2>/dev/null || true
    sleep 86400
done
