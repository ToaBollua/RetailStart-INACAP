import os
import json
import datetime
from sqlalchemy import create_engine, text

PG_URI = "postgresql://retail_user:retail_pass@srv-db-postgres-primary:5432/retail_dw"

def audit():
    engine = create_engine(PG_URI)
    report = {}
    
    with engine.connect() as conn:
        # 1. Row counts
        tables = ['dim_cliente', 'dim_producto', 'dim_tiempo', 'dim_canal', 'fact_ventas', 'fact_events']
        counts = {}
        for t in tables:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {t}"))
            counts[t] = res.scalar()
        report['counts'] = counts
        
        # 2. Sums of sales
        sum_fact_ventas = conn.execute(text("SELECT SUM(total) FROM fact_ventas")).scalar()
        sum_fact_events = conn.execute(text("SELECT SUM((data->>'precio')::NUMERIC) FROM fact_events")).scalar()
        
        report['sales_sums'] = {
            'fact_ventas': float(sum_fact_ventas or 0),
            'fact_events': float(sum_fact_events or 0)
        }
        
        # 3. Analyze simulation events (TX-SIM-%)
        # Check total simulated events
        sim_events_count = conn.execute(text("SELECT COUNT(*) FROM fact_events WHERE id LIKE 'TX-SIM-%'")).scalar()
        
        # Check if they contain placeholders like "Desconocido" or "sin_canal" or -1
        placeholders_in_sim = conn.execute(text("""
            SELECT COUNT(*) FROM fact_events 
            WHERE id LIKE 'TX-SIM-%' 
              AND (
                data->>'cliente' = 'Desconocido' 
                OR data->>'producto' = 'Desconocido' 
                OR data->>'canal' = 'sin_canal' 
                OR (data->>'precio')::NUMERIC = -1
              )
        """)).scalar()
        
        # Let's also check if there are nulls or empty values in key fields
        nulls_in_sim = conn.execute(text("""
            SELECT COUNT(*) FROM fact_events 
            WHERE id LIKE 'TX-SIM-%' 
              AND (
                data->>'cliente' IS NULL 
                OR data->>'producto' IS NULL 
                OR data->>'canal' IS NULL 
                OR data->>'precio' IS NULL
              )
        """)).scalar()
        
        # Sample of 3 simulated events to check format
        sample_res = conn.execute(text("SELECT id, data, processed_at FROM fact_events WHERE id LIKE 'TX-SIM-%' LIMIT 3"))
        samples = []
        for r in sample_res:
            samples.append({
                'id': r[0],
                'data': r[1],
                'processed_at': str(r[2])
            })
            
        report['simulation_audit'] = {
            'sim_events_count': sim_events_count,
            'placeholders_count': placeholders_in_sim,
            'nulls_count': nulls_in_sim,
            'samples': samples
        }
        
        # 4. Check 5-day incremental events vs fact_ventas
        # POS: 10 transactions
        pos_ventas_count = conn.execute(text("SELECT COUNT(*) FROM fact_ventas WHERE id_transaccion LIKE 'POS-%'")).scalar()
        pos_events_count = conn.execute(text("SELECT COUNT(*) FROM fact_events WHERE id LIKE 'POS-%'")).scalar()
        
        # Online: 10 transactions
        online_ventas_count = conn.execute(text("SELECT COUNT(*) FROM fact_ventas WHERE id_transaccion LIKE 'WEB-%'")).scalar()
        online_events_count = conn.execute(text("SELECT COUNT(*) FROM fact_events WHERE id LIKE 'WEB-%'")).scalar()
        
        report['incremental_5days'] = {
            'pos_ventas': pos_ventas_count,
            'pos_events': pos_events_count,
            'online_ventas': online_ventas_count,
            'online_events': online_events_count
        }

    # 5. Check backups on the host
    backups_dir = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP/backups"
    backup_files = []
    if os.path.exists(backups_dir):
        for f in os.listdir(backups_dir):
            if f.endswith('.tar.gz'):
                path = os.path.join(backups_dir, f)
                stat = os.stat(path)
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                backup_files.append({
                    'filename': f,
                    'size_bytes': stat.st_size,
                    'modified_time': mtime.isoformat()
                })
    
    report['backups'] = {
        'total_files': len(backup_files),
        'files': backup_files,
        'purge_policy': 'Files older than 7 days (find -mtime +7) are deleted daily.'
    }
    
    print(json.dumps(report, indent=4))

if __name__ == '__main__':
    audit()
