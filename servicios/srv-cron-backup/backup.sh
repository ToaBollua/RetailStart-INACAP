#!/bin/bash
while true; do
    TS=$(date +%Y%m%d_%H%M%S)
    echo "[CRON] Extrayendo volúmenes a /backups..."
    tar -czf /backups/mongo_${TS}.tar.gz -C /data/mongo . 2>/dev/null || true
    tar -czf /backups/postgres_${TS}.tar.gz -C /data/postgres . 2>/dev/null || true
    
    echo "[CRON] Aplicando política de purga de backups antiguos (+7 días)..."
    find /backups -type f -name '*.tar.gz' -mtime +7 -print -delete
    
    sleep 86400
done
