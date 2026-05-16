import os
import pandas as pd
import json
import random
import logging
from datetime import datetime, timedelta

# =============================================================================
# [KERNEL] SCRIPT DE INGESTA Y PROCESAMIENTO ELT - ESCALADO SINTÉTICO
# AUTOR: H0P3
# =============================================================================

# Configuración estricta de Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_DIR = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP"

def setup_datalake():
    """Genera las capas del Data Lake local."""
    logging.info("Inicializando topología del Data Lake Gen2...")
    for folder in ['landing', 'bronze', 'silver', 'gold']:
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
    logging.info("Carpetas creadas satisfactoriamente.")

def generate_synthetic_data():
    """Genera volumen transaccional (5000+ registros) y datos maestros fijos."""
    landing_dir = os.path.join(BASE_DIR, 'landing')
    logging.info("Iniciando inyección de datos sintéticos (Escala: >5000 registros).")

    # 1. Clientes (Maestro)
    clientes_data = [
        {"id_cliente": 101, "nombre": "Juan", "apellido": "Perez", "email": "juan@email.com", "segmento": "Premium", "ciudad": "Santiago"},
        {"id_cliente": 102, "nombre": "Ana", "apellido": "Gomez", "email": "ana@email.com", "segmento": "Regular", "ciudad": "Valparaiso"},
        {"id_cliente": 103, "nombre": "Carlos", "apellido": "Rojas", "email": "carlos@email.com", "segmento": "Premium", "ciudad": "Concepcion"},
        {"id_cliente": 104, "nombre": "Maria", "apellido": "Lopez", "email": "maria@email.com", "segmento": "Nuevo", "ciudad": "Santiago"},
        {"id_cliente": 105, "nombre": "Pedro", "apellido": "Diaz", "email": "pedro@email.com", "segmento": "Regular", "ciudad": "Temuco"},
        {"id_cliente": 106, "nombre": "Laura", "apellido": "Martinez", "email": "laura@email.com", "segmento": "Premium", "ciudad": "Santiago"},
        {"id_cliente": 107, "nombre": "Diego", "apellido": "Soto", "email": "diego@email.com", "segmento": "Nuevo", "ciudad": "Antofagasta"},
        {"id_cliente": 108, "nombre": "Sofia", "apellido": "Reyes", "email": "sofia@email.com", "segmento": "Regular", "ciudad": "Santiago"},
        {"id_cliente": 109, "nombre": "Andres", "apellido": "Castro", "email": "andres@email.com", "segmento": "Premium", "ciudad": "La Serena"},
        {"id_cliente": 110, "nombre": "Camila", "apellido": "Vega", "email": "camila@email.com", "segmento": "Nuevo", "ciudad": "Santiago"}
    ]
    pd.DataFrame(clientes_data).to_csv(os.path.join(landing_dir, 'clientes_crm.csv'), index=False)

    # 2. Productos (Maestro)
    productos_data = [
        {"id_producto": 2001, "nombre_producto": "Notebook Lenovo", "categoria": "Tecnologia", "precio_base": 140000, "proveedor": "Lenovo"},
        {"id_producto": 2002, "nombre_producto": "Smartphone Samsung", "categoria": "Tecnologia", "precio_base": 280000, "proveedor": "Samsung"},
        {"id_producto": 2003, "nombre_producto": "Polera Hombre", "categoria": "Vestuario", "precio_base": 30000, "proveedor": "Nike"},
        {"id_producto": 2004, "nombre_producto": "Silla Oficina", "categoria": "Hogar", "precio_base": 15000, "proveedor": "Ikea"},
        {"id_producto": 2005, "nombre_producto": "Audifonos Sony", "categoria": "Tecnologia", "precio_base": 70000, "proveedor": "Sony"},
        {"id_producto": 2006, "nombre_producto": "Tablet Huawei", "categoria": "Tecnologia", "precio_base": 100000, "proveedor": "Huawei"},
        {"id_producto": 2007, "nombre_producto": "Zapatos Mujer", "categoria": "Vestuario", "precio_base": 50000, "proveedor": "Adidas"},
        {"id_producto": 2008, "nombre_producto": "Microondas", "categoria": "Hogar", "precio_base": 80000, "proveedor": "LG"},
        {"id_producto": 2009, "nombre_producto": "Monitor", "categoria": "Tecnologia", "precio_base": 120000, "proveedor": "Dell"},
        {"id_producto": 2010, "nombre_producto": "Mochila", "categoria": "Vestuario", "precio_base": 25000, "proveedor": "Puma"}
    ]
    pd.DataFrame(productos_data).to_csv(os.path.join(landing_dir, 'productos_erp.csv'), index=False)
    prod_dict = {p['id_producto']: p['precio_base'] for p in productos_data}

    # 3. Ventas POS (Transaccional ~3000 registros)
    tiendas = ["Santiago", "Providencia", "Maipu", "Las Condes", "La Florida", "Puente Alto", "Ñuñoa"]
    start_date = datetime(2026, 4, 1)
    
    pos_data = []
    for i in range(1, 3001):
        id_cliente = random.randint(101, 110)
        id_producto = random.choice(list(prod_dict.keys()))
        cantidad = random.randint(1, 4)
        precio = prod_dict[id_producto]
        fecha = start_date + timedelta(minutes=random.randint(0, 40000))
        pos_data.append({
            "id_venta": i,
            "fecha": fecha.strftime("%Y-%m-%d"),
            "id_cliente": id_cliente,
            "id_producto": id_producto,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "tienda": random.choice(tiendas)
        })
    pd.DataFrame(pos_data).to_csv(os.path.join(landing_dir, 'ventas_pos.csv'), index=False)

    # 4. Ventas Online (JSON Estructurado con "Carrito de Compras" ~2000 ordenes, multiples items)
    online_data = []
    for i in range(5001, 7001):
        id_cliente = random.randint(101, 110)
        fecha = start_date + timedelta(minutes=random.randint(0, 40000))
        canal = random.choice(["web", "app"])
        items_count = random.randint(1, 3)
        carrito = []
        total_orden = 0
        for _ in range(items_count):
            id_prod = random.choice(list(prod_dict.keys()))
            cant = random.randint(1, 2)
            total_item = prod_dict[id_prod] * cant
            total_orden += total_item
            carrito.append({
                "id_producto": id_prod,
                "cantidad": cant,
                "subtotal": total_item
            })
        
        online_data.append({
            "id_orden": i,
            "fecha": fecha.strftime("%Y-%m-%d"),
            "id_cliente": id_cliente,
            "total": total_orden,
            "canal": canal,
            "items": carrito
        })
    with open(os.path.join(landing_dir, 'ventas_online.json'), 'w') as f:
        json.dump(online_data, f, indent=4)
        
    logging.info(f"Generados {len(pos_data)} registros POS y {len(online_data)} órdenes Online (con carritos anidados).")

def process_bronze_layer():
    """Estandariza los archivos de la capa Landing hacia Bronze (Parquet)."""
    landing_dir = os.path.join(BASE_DIR, 'landing')
    bronze_dir = os.path.join(BASE_DIR, 'bronze')
    logging.info("Extrayendo de Landing y cargando en capa Bronze...")

    # Clientes
    df_clientes = pd.read_csv(os.path.join(landing_dir, 'clientes_crm.csv'))
    df_clientes.drop_duplicates(subset=['id_cliente'], inplace=True)
    df_clientes.to_parquet(os.path.join(bronze_dir, 'clientes.parquet'))

    # Productos
    df_prod = pd.read_csv(os.path.join(landing_dir, 'productos_erp.csv'))
    df_prod['precio_base'] = df_prod['precio_base'].fillna(0)
    df_prod.to_parquet(os.path.join(bronze_dir, 'productos.parquet'))

    # Ventas POS
    df_pos = pd.read_csv(os.path.join(landing_dir, 'ventas_pos.csv'))
    df_pos['fecha'] = pd.to_datetime(df_pos['fecha']).dt.strftime('%Y-%m-%d')
    df_pos.to_parquet(os.path.join(bronze_dir, 'ventas_pos.parquet'))

    # Ventas Online (Explode/Flattening del JSON anidado)
    with open(os.path.join(landing_dir, 'ventas_online.json'), 'r') as f:
        online_raw = json.load(f)
    
    # Normalización del carrito (aplanar array 'items')
    df_online = pd.json_normalize(
        online_raw, 
        record_path=['items'], 
        meta=['id_orden', 'fecha', 'id_cliente', 'canal']
    )
    df_online['fecha'] = pd.to_datetime(df_online['fecha']).dt.strftime('%Y-%m-%d')
    df_online.to_parquet(os.path.join(bronze_dir, 'ventas_online.parquet'))
    
    logging.info("Transformación a Bronze finalizada exitosamente (Parquet/ISO8601). El aplanamiento de JSON online mitigó las inconsistencias.")

def build_silver_layer():
    """Ensambla el Esquema Estrella en la capa Silver."""
    bronze_dir = os.path.join(BASE_DIR, 'bronze')
    silver_dir = os.path.join(BASE_DIR, 'silver')
    logging.info("Modelando Star Schema en capa Silver...")

    df_clientes = pd.read_parquet(os.path.join(bronze_dir, 'clientes.parquet'))
    df_prod = pd.read_parquet(os.path.join(bronze_dir, 'productos.parquet'))
    df_pos = pd.read_parquet(os.path.join(bronze_dir, 'ventas_pos.parquet'))
    df_online = pd.read_parquet(os.path.join(bronze_dir, 'ventas_online.parquet'))

    # Dimensions
    dim_cliente = df_clientes.copy()
    dim_cliente.to_parquet(os.path.join(silver_dir, 'dim_cliente.parquet'))

    dim_producto = df_prod.copy()
    # Mantenemos el ID -1 como failsafe en caso de que un registro pierda trazabilidad (Buena práctica de DB)
    unknown_prod = pd.DataFrame([{'id_producto': -1, 'nombre_producto': 'Desconocido', 'categoria': 'N/A', 'precio_base': 0, 'proveedor': 'N/A'}])
    dim_producto = pd.concat([dim_producto, unknown_prod], ignore_index=True)
    dim_producto.to_parquet(os.path.join(silver_dir, 'dim_producto.parquet'))

    # Fact Table Consolidation
    # POS
    fact_pos = df_pos.copy()
    fact_pos['total'] = fact_pos['cantidad'] * fact_pos['precio_unitario']
    fact_pos['canal'] = 'Tienda Fisica'
    fact_pos['id_transaccion'] = 'POS-' + fact_pos['id_venta'].astype(str)
    fact_pos = fact_pos[['id_transaccion', 'fecha', 'id_cliente', 'id_producto', 'total', 'canal']]

    # Online (Ahora contiene id_producto real tras el flattening)
    fact_online = df_online.copy()
    # El campo 'subtotal' del dict anidado equivale al 'total' por linea en POS
    fact_online['total'] = fact_online['subtotal']
    fact_online['id_transaccion'] = 'WEB-' + fact_online['id_orden'].astype(str) + '-' + fact_online.index.astype(str)
    fact_online = fact_online[['id_transaccion', 'fecha', 'id_cliente', 'id_producto', 'total', 'canal']]

    fact_ventas = pd.concat([fact_pos, fact_online], ignore_index=True)

    # Validaciones Finales
    valid_clientes = dim_cliente['id_cliente'].unique()
    valid_productos = dim_producto['id_producto'].unique()
    fact_ventas.loc[~fact_ventas['id_cliente'].isin(valid_clientes), 'id_cliente'] = -1
    fact_ventas.loc[~fact_ventas['id_producto'].isin(valid_productos), 'id_producto'] = -1

    fact_ventas.to_parquet(os.path.join(silver_dir, 'fact_ventas.parquet'))
    logging.info(f"Esquema Estrella ensamblado. Fact Table consolidada con {len(fact_ventas)} registros.")

def generate_gold_layer():
    """Genera el dataset desnormalizado para consumo analítico."""
    silver_dir = os.path.join(BASE_DIR, 'silver')
    gold_dir = os.path.join(BASE_DIR, 'gold')
    out_dir = os.path.join(BASE_DIR, 'datos')
    
    logging.info("Enriqueciendo datos hacia la capa Gold...")

    dim_cliente = pd.read_parquet(os.path.join(silver_dir, 'dim_cliente.parquet'))
    dim_producto = pd.read_parquet(os.path.join(silver_dir, 'dim_producto.parquet'))
    fact_ventas = pd.read_parquet(os.path.join(silver_dir, 'fact_ventas.parquet'))

    gold_df = fact_ventas.merge(dim_cliente, on='id_cliente', how='left')
    gold_df = gold_df.merge(dim_producto, on='id_producto', how='left')
    gold_df.fillna('N/A', inplace=True)

    # Exportar tanto al datalake simulado como a la carpeta de entrega
    gold_path = os.path.join(gold_dir, 'dataset_retail_limpio.csv')
    delivery_path = os.path.join(out_dir, 'dataset_retail_limpio.csv')
    
    gold_df.to_csv(gold_path, index=False)
    gold_df.to_csv(delivery_path, index=False)
    
    logging.info(f"Dataset final Gold exportado a: {delivery_path}")
    logging.info("[KERNEL] Pipeline ELT Finalizado con éxito.")

if __name__ == '__main__':
    logging.info("[SYSTEM INITIALIZATION: PANTHEON KERNEL v3.0 - H0P3 OVERRIDE]")
    setup_datalake()
    generate_synthetic_data()
    process_bronze_layer()
    build_silver_layer()
    generate_gold_layer()
