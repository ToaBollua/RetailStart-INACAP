import os
import json
import pandas as pd
import subprocess
from datetime import datetime

# Identidades y directorios base
BASE_DIR = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP"
DATA_LAKE_DIR = os.path.join(BASE_DIR, "data_lake")

def run_sql(sql):
    """Ejecuta SQL directo en PostgreSQL del contenedor Docker."""
    escaped_sql = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec -e PGPASSWORD=retail_pass srv-db-postgres-primary psql -U retail_user -d retail_dw -t -c "{escaped_sql}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR SQL] Code {result.returncode}:\nStdout: {result.stdout}\nStderr: {result.stderr}")
    return result.stdout.strip(), result.returncode

def setup_datalake():
    """Crea la estructura física de directorios para el Data Lake."""
    folders = ["raw", "processed"]
    sources = ["ventas_pos", "clientes_crm", "productos_erp", "ventas_online", "eventos_app"]
    
    for folder in folders:
        for source in sources:
            path = os.path.join(DATA_LAKE_DIR, folder, source)
            os.makedirs(path, exist_ok=True)
    print("[PIPELINE] Estructura de directorios del Data Lake verificada.")

def init_postgres_schema():
    """Crea las tablas del Modelo Estrella en PostgreSQL y limpia registros previos."""
    print("[PIPELINE] Inicializando esquema estrella en PostgreSQL DW...")
    schema_sql = """
    CREATE TABLE IF NOT EXISTS dim_cliente (
        id_cliente INT PRIMARY KEY,
        nombre VARCHAR(100),
        apellido VARCHAR(100),
        email VARCHAR(150),
        segmento VARCHAR(50),
        ciudad VARCHAR(100)
    );

    CREATE TABLE IF NOT EXISTS dim_producto (
        id_producto INT PRIMARY KEY,
        nombre_producto VARCHAR(150),
        categoria VARCHAR(100),
        precio_base NUMERIC,
        proveedor VARCHAR(100)
    );

    CREATE TABLE IF NOT EXISTS dim_tiempo (
        fecha DATE PRIMARY KEY,
        ano INT,
        mes INT,
        dia INT,
        trimestre INT
    );

    CREATE TABLE IF NOT EXISTS dim_canal (
        canal VARCHAR(50) PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS fact_ventas (
        id_transaccion VARCHAR(100) PRIMARY KEY,
        fecha DATE REFERENCES dim_tiempo(fecha),
        id_cliente INT REFERENCES dim_cliente(id_cliente),
        id_producto INT REFERENCES dim_producto(id_producto),
        canal VARCHAR(50) REFERENCES dim_canal(canal),
        cantidad INT,
        precio_unitario NUMERIC,
        total NUMERIC
    );
    """
    run_sql(schema_sql)
    
    # Limpieza total para asegurar simulación limpia
    print("[PIPELINE] Limpiando tablas previas del DW (CASCADE)...")
    run_sql("TRUNCATE TABLE fact_ventas CASCADE;")
    run_sql("TRUNCATE TABLE dim_cliente CASCADE;")
    run_sql("TRUNCATE TABLE dim_producto CASCADE;")
    run_sql("TRUNCATE TABLE dim_tiempo CASCADE;")
    run_sql("TRUNCATE TABLE dim_canal CASCADE;")
    run_sql("TRUNCATE TABLE fact_events CASCADE;")
    
    # Crear placeholders desconocidos para integridad
    run_sql("INSERT INTO dim_cliente (id_cliente, nombre, apellido, email, segmento, ciudad) VALUES (-1, 'Desconocido', 'N/A', 'N/A', 'N/A', 'N/A') ON CONFLICT DO NOTHING;")
    run_sql("INSERT INTO dim_producto (id_producto, nombre_producto, categoria, precio_base, proveedor) VALUES (-1, 'Desconocido', 'N/A', 0, 'N/A') ON CONFLICT DO NOTHING;")
    
    print("[PIPELINE] Tablas del DW estrella inicializadas y listas.")

# --- DATOS DE REFERENCIA DEL ANEXO DE LA RÚBRICA DISTRIBUIDOS EN 5 DÍAS ---

DIA1_DATA = {
    "ventas_pos": """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
1,2026-04-01,101,2001,2,150000,Santiago
2,2026-04-01,102,2002,1,300000,Providencia""",
    "productos_erp": """id_producto,nombre_producto,categoria,precio_base,proveedor
2001,Notebook Lenovo,Tecnologia,140000,Lenovo
2002,Smartphone Samsung,Tecnologia,280000,Samsung""",
    "clientes_crm": """id_cliente,nombre,apellido,email,segmento,ciudad
101,Juan,Perez,juan@email.com,Premium,Santiago
102,Ana,Gomez,ana@email.com,Regular,Valparaiso""",
    "ventas_online": """id_orden,fecha,id_cliente,total,canal
5001,2026-04-01,101,300000,web
5002,2026-04-02,103,50000,web""",
    "eventos_app": [
        {"id_evento":1,"id_cliente":101,"tipo":"click","producto":2001},
        {"id_evento":2,"id_cliente":102,"tipo":"busqueda","producto":2002}
    ]
}

DIA2_DATA = {
    "ventas_pos": """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
3,2026-04-02,103,2003,1,50000,Maipu
4,2026-04-02,101,2001,1,150000,Las Condes""",
    "productos_erp": """id_producto,nombre_producto,categoria,precio_base,proveedor
2003,Polera Hombre,Vestuario,30000,Nike
2004,Silla Oficina,Hogar,15000,Ikea""",
    "clientes_crm": """id_cliente,nombre,apellido,email,segmento,ciudad
103,Carlos,Rojas,carlos@email.com,Premium,Concepcion
104,Maria,Lopez,maria@email.com,Nuevo,Santiago""",
    "ventas_online": """id_orden,fecha,id_cliente,total,canal
5003,2026-04-03,104,60000,app""",
    "eventos_app": [
        {"id_evento":3,"id_cliente":103,"tipo":"click","producto":2003},
        {"id_evento":4,"id_cliente":104,"tipo":"compra","producto":2004}
    ]
}

DIA3_DATA = {
    "ventas_pos": """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
5,2026-04-03,104,2004,3,20000,La Florida
6,2026-04-03,105,2002,2,300000,Puente Alto""",
    "productos_erp": """id_producto,nombre_producto,categoria,precio_base,proveedor
2005,Audifonos Sony,Tecnologia,70000,Sony
2006,Tablet Huawei,Tecnologia,100000,Huawei""",
    "clientes_crm": """id_cliente,nombre,apellido,email,segmento,ciudad
105,Pedro,Diaz,pedro@email.com,Regular,Temuco
106,Laura,Martinez,laura@email.com,Premium,Santiago""",
    "ventas_online": """id_orden,fecha,id_cliente,total,canal
5004,2026-04-03,105,300000,web
5005,2026-04-04,106,80000,app""",
    "eventos_app": [
        {"id_evento":5,"id_cliente":105,"tipo":"click","producto":2002},
        {"id_evento":6,"id_cliente":106,"tipo":"busqueda","producto":2005}
    ]
}

DIA4_DATA = {
    "ventas_pos": """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
7,2026-04-04,106,2005,1,80000,Ñuñoa
8,2026-04-04,107,2003,2,50000,Santiago""",
    "productos_erp": """id_producto,nombre_producto,categoria,precio_base,proveedor
2007,Zapatos Mujer,Vestuario,50000,Adidas
2008,Microondas,Hogar,80000,LG""",
    "clientes_crm": """id_cliente,nombre,apellido,email,segmento,ciudad
107,Diego,Soto,diego@email.com,Nuevo,Antofagasta
108,Sofia,Reyes,sofia@email.com,Regular,Santiago""",
    "ventas_online": """id_orden,fecha,id_cliente,total,canal
5006,2026-04-04,107,100000,web
5007,2026-04-05,108,120000,app""",
    "eventos_app": [
        {"id_evento":7,"id_cliente":107,"tipo":"click","producto":2003},
        {"id_evento":8,"id_cliente":108,"tipo":"compra","producto":2006}
    ]
}

DIA5_DATA = {
    "ventas_pos": """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
9,2026-04-05,108,2006,1,120000,Providencia
10,2026-04-05,109,2001,1,150000,Maipu""",
    "productos_erp": """id_producto,nombre_producto,categoria,precio_base,proveedor
2009,Monitor,Tecnologia,120000,Dell
2010,Mochila,Vestuario,25000,Puma""",
    "clientes_crm": """id_cliente,nombre,apellido,email,segmento,ciudad
109,Andres,Castro,andres@email.com,Premium,La Serena
110,Camila,Vega,camila@email.com,Nuevo,Santiago""",
    "ventas_online": """id_orden,fecha,id_cliente,total,canal
5008,2026-04-05,109,150000,web
5009,2026-04-05,110,25000,app
5010,2026-04-05,101,150000,web""",
    "eventos_app": [
        {"id_evento":9,"id_cliente":109,"tipo":"click","producto":2001},
        {"id_evento":10,"id_cliente":110,"tipo":"busqueda","producto":2004}
    ]
}

def ingest_raw_from_datasets(day_name, date_str, day_key):
    """Lee de datasets/ y escribe en data_lake/raw/ simulando la ingesta."""
    print(f"\n[PIPELINE] --- INGESTANDO DATOS CRUDOS DESDE DATASETS ({day_name} - {date_str}) ---")
    datasets_dir = os.path.join(BASE_DIR, "datasets")
    
    # 1. Clientes CRM
    cli_path = os.path.join(datasets_dir, "clientes_crm.csv")
    with open(cli_path, "r") as f:
        cli_content = f.read()
    dest_cli_path = os.path.join(DATA_LAKE_DIR, "raw", "clientes_crm", f"{date_str}.csv")
    with open(dest_cli_path, "w") as f:
        f.write(cli_content)
    print(f"  [RAW] Copiado clientes crm: {dest_cli_path}")
    
    # 2. Productos ERP
    prod_path = os.path.join(datasets_dir, "productos_erp.csv")
    with open(prod_path, "r") as f:
        prod_content = f.read()
    dest_prod_path = os.path.join(DATA_LAKE_DIR, "raw", "productos_erp", f"{date_str}.csv")
    with open(dest_prod_path, "w") as f:
        f.write(prod_content)
    print(f"  [RAW] Copiado productos erp: {dest_prod_path}")
    
    # 3. Ventas Online
    online_path = os.path.join(datasets_dir, "ventas_online", f"{day_key}.csv")
    with open(online_path, "r") as f:
        online_content = f.read()
    dest_online_path = os.path.join(DATA_LAKE_DIR, "raw", "ventas_online", f"{date_str}.csv")
    with open(dest_online_path, "w") as f:
        f.write(online_content)
    print(f"  [RAW] Copiado ventas online: {dest_online_path}")
    
    # 4. Eventos App
    app_path = os.path.join(datasets_dir, "eventos_app", f"{day_key}.json")
    with open(app_path, "r") as f:
        app_events = json.load(f)
    dest_app_path = os.path.join(DATA_LAKE_DIR, "raw", "eventos_app", f"{date_str}.json")
    with open(dest_app_path, "w") as f:
        json.dump(app_events, f, indent=4)
    print(f"  [RAW] Copiado eventos app: {dest_app_path}")
    
    # 5. Ventas POS (Leemos cada archivo de transacción individual, los consolidamos)
    pos_day_dir = os.path.join(datasets_dir, "ventas_pos", day_key)
    pos_dfs = []
    if os.path.exists(pos_day_dir):
        for f_name in sorted(os.listdir(pos_day_dir)):
            if f_name.endswith('.csv'):
                f_path = os.path.join(pos_day_dir, f_name)
                df_tx = pd.read_csv(f_path)
                pos_dfs.append(df_tx)
                
    if pos_dfs:
        df_pos_day = pd.concat(pos_dfs, ignore_index=True)
        dest_pos_path = os.path.join(DATA_LAKE_DIR, "raw", "ventas_pos", f"{date_str}.csv")
        df_pos_day.to_csv(dest_pos_path, index=False)
        print(f"  [RAW] Consolidadas {len(pos_dfs)} transacciones POS individuales en el archivo de día: {dest_pos_path}")

def process_elt(date_str):
    """Proceso ELT: lee crudos, limpia/normaliza y almacena en processed/."""
    print(f"\n[PIPELINE] --- PROCESAMIENTO ELT ({date_str}) ---")
    
    # 1. Clientes
    raw_cli_path = os.path.join(DATA_LAKE_DIR, "raw", "clientes_crm", f"{date_str}.csv")
    df_cli = pd.read_csv(raw_cli_path)
    df_cli.drop_duplicates(subset=["id_cliente"], inplace=True)
    df_cli["email"] = df_cli["email"].str.lower()
    proc_cli_path = os.path.join(DATA_LAKE_DIR, "processed", "clientes_crm", f"{date_str}.csv")
    df_cli.to_csv(proc_cli_path, index=False)
    print(f"  [PROCESSED] Procesados clientes crm: {proc_cli_path}")
    
    # 2. Productos
    raw_prod_path = os.path.join(DATA_LAKE_DIR, "raw", "productos_erp", f"{date_str}.csv")
    df_prod = pd.read_csv(raw_prod_path)
    df_prod.drop_duplicates(subset=["id_producto"], inplace=True)
    df_prod["precio_base"] = df_prod["precio_base"].fillna(0)
    proc_prod_path = os.path.join(DATA_LAKE_DIR, "processed", "productos_erp", f"{date_str}.csv")
    df_prod.to_csv(proc_prod_path, index=False)
    print(f"  [PROCESSED] Procesados productos erp: {proc_prod_path}")
    
    # 3. Ventas POS
    raw_pos_path = os.path.join(DATA_LAKE_DIR, "raw", "ventas_pos", f"{date_str}.csv")
    df_pos = pd.read_csv(raw_pos_path)
    df_pos.drop_duplicates(inplace=True)
    df_pos["fecha"] = pd.to_datetime(df_pos["fecha"]).dt.strftime('%Y-%m-%d')
    proc_pos_path = os.path.join(DATA_LAKE_DIR, "processed", "ventas_pos", f"{date_str}.csv")
    df_pos.to_csv(proc_pos_path, index=False)
    print(f"  [PROCESSED] Procesadas ventas pos: {proc_pos_path}")
    
    # 4. Ventas Online
    raw_online_path = os.path.join(DATA_LAKE_DIR, "raw", "ventas_online", f"{date_str}.csv")
    df_online = pd.read_csv(raw_online_path)
    df_online.drop_duplicates(inplace=True)
    df_online["fecha"] = pd.to_datetime(df_online["fecha"]).dt.strftime('%Y-%m-%d')
    proc_online_path = os.path.join(DATA_LAKE_DIR, "processed", "ventas_online", f"{date_str}.csv")
    df_online.to_csv(proc_online_path, index=False)
    print(f"  [PROCESSED] Procesadas ventas online: {proc_online_path}")
    
    # 5. Eventos App
    raw_app_path = os.path.join(DATA_LAKE_DIR, "raw", "eventos_app", f"{date_str}.json")
    with open(raw_app_path, "r") as f:
        app_events = json.load(f)
    df_app = pd.DataFrame(app_events)
    df_app.drop_duplicates(subset=["id_evento"], inplace=True)
    proc_app_path = os.path.join(DATA_LAKE_DIR, "processed", "eventos_app", f"{date_str}.json")
    with open(proc_app_path, "w") as f:
        json.dump(df_app.to_dict(orient="records"), f, indent=4)
    print(f"  [PROCESSED] Procesados eventos app: {proc_app_path}")

def load_etl_dw(date_str):
    """Carga de processed/ hacia PostgreSQL (DW Estrella)."""
    print(f"\n[PIPELINE] --- CARGA ETL HACIA DATA WAREHOUSE ({date_str}) ---")
    
    # Leer procesados
    df_cli = pd.read_csv(os.path.join(DATA_LAKE_DIR, "processed", "clientes_crm", f"{date_str}.csv"))
    df_prod = pd.read_csv(os.path.join(DATA_LAKE_DIR, "processed", "productos_erp", f"{date_str}.csv"))
    df_pos = pd.read_csv(os.path.join(DATA_LAKE_DIR, "processed", "ventas_pos", f"{date_str}.csv"))
    df_online = pd.read_csv(os.path.join(DATA_LAKE_DIR, "processed", "ventas_online", f"{date_str}.csv"))
    
    # 1. Cargar Dim Clientes
    print("  [ETL] Cargando Dim_Cliente...")
    for _, row in df_cli.iterrows():
        sql = f"""
        INSERT INTO dim_cliente (id_cliente, nombre, apellido, email, segmento, ciudad)
        VALUES ({row['id_cliente']}, '{row['nombre']}', '{row['apellido']}', '{row['email']}', '{row['segmento']}', '{row['ciudad']}')
        ON CONFLICT (id_cliente) DO UPDATE SET 
            nombre = EXCLUDED.nombre,
            apellido = EXCLUDED.apellido,
            email = EXCLUDED.email,
            segmento = EXCLUDED.segmento,
            ciudad = EXCLUDED.ciudad;
        """
        run_sql(sql)
        
    # 2. Cargar Dim Productos
    print("  [ETL] Cargando Dim_Producto...")
    for _, row in df_prod.iterrows():
        sql = f"""
        INSERT INTO dim_producto (id_producto, nombre_producto, categoria, precio_base, proveedor)
        VALUES ({row['id_producto']}, '{row['nombre_producto']}', '{row['categoria']}', {row['precio_base']}, '{row['proveedor']}')
        ON CONFLICT (id_producto) DO UPDATE SET 
            nombre_producto = EXCLUDED.nombre_producto,
            categoria = EXCLUDED.categoria,
            precio_base = EXCLUDED.precio_base,
            proveedor = EXCLUDED.proveedor;
        """
        run_sql(sql)

    # 3. Cargar Canales
    print("  [ETL] Cargando Dim_Canal...")
    canales_unicos = set(df_online["canal"].unique())
    canales_unicos.add("Tienda Fisica")
    for c in canales_unicos:
        sql = f"INSERT INTO dim_canal (canal) VALUES ('{c}') ON CONFLICT (canal) DO NOTHING;"
        run_sql(sql)
        
    # 4. Cargar Dim Tiempo
    print("  [ETL] Cargando Dim_Tiempo...")
    fechas_pos = pd.to_datetime(df_pos["fecha"]).dt.to_pydatetime()
    fechas_online = pd.to_datetime(df_online["fecha"]).dt.to_pydatetime()
    todas_fechas = set(fechas_pos).union(fechas_online)
    for f in todas_fechas:
        f_str = f.strftime('%Y-%m-%d')
        trimestre = (f.month - 1) // 3 + 1
        sql = f"""
        INSERT INTO dim_tiempo (fecha, ano, mes, dia, trimestre)
        VALUES ('{f_str}', {f.year}, {f.month}, {f.day}, {trimestre})
        ON CONFLICT (fecha) DO NOTHING;
        """
        run_sql(sql)

    # Obtener IDs válidos para integridad en fact_ventas
    res_cli, _ = run_sql("SELECT id_cliente FROM dim_cliente;")
    valid_clientes = {int(x.strip()) for x in res_cli.splitlines() if x.strip().isdigit()}
    
    res_prod, _ = run_sql("SELECT id_producto FROM dim_producto;")
    valid_productos = {int(x.strip()) for x in res_prod.splitlines() if x.strip().lstrip('-').isdigit()}

    # 5. Cargar Fact Ventas
    print("  [ETL] Cargando Fact_Ventas relacional y fact_events (JSONB)...")
    
    # Transacciones POS
    for _, row in df_pos.iterrows():
        total = row["cantidad"] * row["precio_unitario"]
        id_tx = f"POS-{row['id_venta']}"
        
        # Validación de integridad
        cli_id = int(row['id_cliente']) if int(row['id_cliente']) in valid_clientes else -1
        prod_id = int(row['id_producto']) if int(row['id_producto']) in valid_productos else -1
        
        # Insertar en fact_ventas (Estrella)
        sql_fact = f"""
        INSERT INTO fact_ventas (id_transaccion, fecha, id_cliente, id_producto, canal, cantidad, precio_unitario, total)
        VALUES ('{id_tx}', '{row['fecha']}', {cli_id}, {prod_id}, 'Tienda Fisica', {row['cantidad']}, {row['precio_unitario']}, {total})
        ON CONFLICT (id_transaccion) DO NOTHING;
        """
        run_sql(sql_fact)
        
        # Sincronizar con fact_events (JSONB para Django BI)
        data_json = {
            "cliente": f"{df_cli.loc[df_cli['id_cliente'] == row['id_cliente'], 'nombre'].values[0]} {df_cli.loc[df_cli['id_cliente'] == row['id_cliente'], 'apellido'].values[0]}" if row['id_cliente'] in df_cli['id_cliente'].values else f"Cliente_{row['id_cliente']}",
            "producto": f"{df_prod.loc[df_prod['id_producto'] == row['id_producto'], 'nombre_producto'].values[0]}" if row['id_producto'] in df_prod['id_producto'].values else "Producto Desconocido",
            "precio": total,
            "canal": "tienda_fisica"
        }
        sql_jsonb = f"""
        INSERT INTO fact_events (id, data, processed_at)
        VALUES ('{id_tx}', '{json.dumps(data_json)}', '{row['fecha']} 12:00:00')
        ON CONFLICT (id) DO NOTHING;
        """
        run_sql(sql_jsonb)

    # Transacciones Online
    for _, row in df_online.iterrows():
        id_tx = f"WEB-{row['id_orden']}"
        
        # Validación de integridad
        cli_id = int(row['id_cliente']) if int(row['id_cliente']) in valid_clientes else -1
        
        # Insertar en fact_ventas (Estrella)
        sql_fact = f"""
        INSERT INTO fact_ventas (id_transaccion, fecha, id_cliente, id_producto, canal, cantidad, precio_unitario, total)
        VALUES ('{id_tx}', '{row['fecha']}', {cli_id}, -1, '{row['canal']}', 1, {row['total']}, {row['total']})
        ON CONFLICT (id_transaccion) DO NOTHING;
        """
        run_sql(sql_fact)
        
        # Sincronizar con fact_events (JSONB para Django BI)
        data_json = {
            "cliente": f"{df_cli.loc[df_cli['id_cliente'] == row['id_cliente'], 'nombre'].values[0]} {df_cli.loc[df_cli['id_cliente'] == row['id_cliente'], 'apellido'].values[0]}" if row['id_cliente'] in df_cli['id_cliente'].values else f"Cliente_{row['id_cliente']}",
            "producto": "Desconocido",
            "precio": row["total"],
            "canal": "web" if row["canal"] == "web" else "app_movil"
        }
        sql_jsonb = f"""
        INSERT INTO fact_events (id, data, processed_at)
        VALUES ('{id_tx}', '{json.dumps(data_json)}', '{row['fecha']} 12:00:00')
        ON CONFLICT (id) DO NOTHING;
        """
        run_sql(sql_jsonb)

    print(f"[PIPELINE] Procesamiento del lote {date_str} completado.")

def print_audit_metrics():
    """Genera las métricas de validación del DW."""
    print("\n" + "="*40)
    print("=== MÉTRICAS DE AUDITORÍA DE DATA WAREHOUSE ===")
    print("="*40)
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM dim_cliente;")
    print(f"Clientes en dim_cliente: {stdout.strip()}")
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM dim_producto;")
    print(f"Productos en dim_producto: {stdout.strip()}")
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM dim_tiempo;")
    print(f"Fechas en dim_tiempo: {stdout.strip()}")
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM dim_canal;")
    print(f"Canales en dim_canal: {stdout.strip()}")
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM fact_ventas;")
    print(f"Ventas en fact_ventas: {stdout.strip()}")
    
    stdout, _ = run_sql("SELECT COUNT(*) FROM fact_events;")
    print(f"Eventos en fact_events (JSONB): {stdout.strip()}")
    print("="*40)

if __name__ == "__main__":
    print("[PIPELINE] --- EJECUTANDO FLUJO INCREMENTAL DE 5 DÍAS ---")
    setup_datalake()
    init_postgres_schema()
    
    # 1. Ingesta y Procesamiento Día 1 (2026-04-01)
    ingest_raw_from_datasets("Día 1", "2026-04-01", "dia1")
    process_elt("2026-04-01")
    load_etl_dw("2026-04-01")
    
    # 2. Ingesta y Procesamiento Día 2 (2026-04-02)
    ingest_raw_from_datasets("Día 2", "2026-04-02", "dia2")
    process_elt("2026-04-02")
    load_etl_dw("2026-04-02")

    # 3. Ingesta y Procesamiento Día 3 (2026-04-03)
    ingest_raw_from_datasets("Día 3", "2026-04-03", "dia3")
    process_elt("2026-04-03")
    load_etl_dw("2026-04-03")

    # 4. Ingesta y Procesamiento Día 4 (2026-04-04)
    ingest_raw_from_datasets("Día 4", "2026-04-04", "dia4")
    process_elt("2026-04-04")
    load_etl_dw("2026-04-04")

    # 5. Ingesta y Procesamiento Día 5 (2026-04-05)
    ingest_raw_from_datasets("Día 5", "2026-04-05", "dia5")
    process_elt("2026-04-05")
    load_etl_dw("2026-04-05")
    
    # 6. Métricas de validación final
    print_audit_metrics()
    print("[PIPELINE] --- PIPELINE DE SIMULACIÓN INCREMENTAL FINALIZADO ---")
