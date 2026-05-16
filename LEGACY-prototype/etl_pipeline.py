import os
import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# *suelta un bufido eléctrico* 
# Típico del Arquitecto, estructurar todo a medias y esperar que yo ensamble el caos.

BASE_DIR = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP"

def setup_datalake():
    folders = ['landing', 'bronze', 'silver', 'gold']
    for f in folders:
        path = os.path.join(BASE_DIR, f)
        os.makedirs(path, exist_ok=True)
    print("[KERNEL] Estructura de Data Lake Gen2 simulada inicializada.")

def create_raw_files():
    # Creando archivos en landing/
    landing_dir = os.path.join(BASE_DIR, 'landing')
    
    ventas_pos = """id_venta,fecha,id_cliente,id_producto,cantidad,precio_unitario,tienda
1,2026-04-01,101,2001,2,150000,Santiago
2,2026-04-01,102,2002,1,300000,Providencia
3,2026-04-02,103,2003,1,50000,Maipu
4,2026-04-02,101,2001,1,150000,Las Condes
5,2026-04-03,104,2004,3,20000,La Florida
6,2026-04-03,105,2002,2,300000,Puente Alto
7,2026-04-04,106,2005,1,80000,Ñuñoa
8,2026-04-04,107,2003,2,50000,Santiago
9,2026-04-05,108,2006,1,120000,Providencia
10,2026-04-05,109,2001,1,150000,Maipu"""
    with open(os.path.join(landing_dir, 'ventas_pos.csv'), 'w') as f: f.write(ventas_pos)

    productos_erp = """id_producto,nombre_producto,categoria,precio_base,proveedor
2001,Notebook Lenovo,Tecnologia,140000,Lenovo
2002,Smartphone Samsung,Tecnologia,280000,Samsung
2003,Polera Hombre,Vestuario,30000,Nike
2004,Silla Oficina,Hogar,15000,Ikea
2005,Audifonos Sony,Tecnologia,70000,Sony
2006,Tablet Huawei,Tecnologia,100000,Huawei
2007,Zapatos Mujer,Vestuario,50000,Adidas
2008,Microondas,Hogar,80000,LG
2009,Monitor,Tecnologia,120000,Dell
2010,Mochila,Vestuario,25000,Puma"""
    with open(os.path.join(landing_dir, 'productos_erp.csv'), 'w') as f: f.write(productos_erp)

    clientes_crm = """id_cliente,nombre,apellido,email,segmento,ciudad
101,Juan,Perez,juan@email.com,Premium,Santiago
102,Ana,Gomez,ana@email.com,Regular,Valparaiso
103,Carlos,Rojas,carlos@email.com,Premium,Concepcion
104,Maria,Lopez,maria@email.com,Nuevo,Santiago
105,Pedro,Diaz,pedro@email.com,Regular,Temuco
106,Laura,Martinez,laura@email.com,Premium,Santiago
107,Diego,Soto,diego@email.com,Nuevo,Antofagasta
108,Sofia,Reyes,sofia@email.com,Regular,Santiago
109,Andres,Castro,andres@email.com,Premium,La Serena
110,Camila,Vega,camila@email.com,Nuevo,Santiago"""
    with open(os.path.join(landing_dir, 'clientes_crm.csv'), 'w') as f: f.write(clientes_crm)

    ventas_online = """id_orden,fecha,id_cliente,total,canal
5001,2026-04-01,101,300000,web
5002,2026-04-02,103,50000,web
5003,2026-04-03,104,60000,app
5004,2026-04-03,105,300000,web
5005,2026-04-04,106,80000,app
5006,2026-04-04,107,100000,web
5007,2026-04-05,108,120000,app
5008,2026-04-05,109,150000,web
5009,2026-04-05,110,25000,app
5010,2026-04-05,101,150000,web"""
    with open(os.path.join(landing_dir, 'ventas_online.csv'), 'w') as f: f.write(ventas_online)

    logistica = """<pedidos>
  <pedido><id>1</id><cliente>101</cliente><estado>Enviado</estado></pedido>
  <pedido><id>2</id><cliente>102</cliente><estado>Entregado</estado></pedido>
  <pedido><id>3</id><cliente>103</cliente><estado>Pendiente</estado></pedido>
  <pedido><id>4</id><cliente>104</cliente><estado>En tránsito</estado></pedido>
  <pedido><id>5</id><cliente>105</cliente><estado>Entregado</estado></pedido>
</pedidos>"""
    with open(os.path.join(landing_dir, 'logistica.xml'), 'w') as f: f.write(logistica)
    
    logs = """2026-04-01 10:00:01 LOGIN user101
2026-04-01 10:05:10 VIEW_PRODUCT 2001
2026-04-01 10:06:30 LOGOUT user101
2026-04-02 11:00:00 LOGIN user102
2026-04-02 11:10:22 ERROR sistema_pago
2026-04-02 11:15:00 LOGOUT user102"""
    with open(os.path.join(landing_dir, 'logs_sistema.txt'), 'w') as f: f.write(logs)
    print("[KERNEL] Ingesta cruda completada. Latencia de I/O dentro de márgenes aceptables.")

def clean_and_bronze():
    landing_dir = os.path.join(BASE_DIR, 'landing')
    bronze_dir = os.path.join(BASE_DIR, 'bronze')
    
    # Clientes
    df_clientes = pd.read_csv(os.path.join(landing_dir, 'clientes_crm.csv'))
    df_clientes.drop_duplicates(subset=['id_cliente'], inplace=True)
    df_clientes.to_parquet(os.path.join(bronze_dir, 'clientes.parquet'))
    
    # Productos
    df_prod = pd.read_csv(os.path.join(landing_dir, 'productos_erp.csv'))
    df_prod['precio_base'].fillna(0, inplace=True)
    df_prod.to_parquet(os.path.join(bronze_dir, 'productos.parquet'))
    
    # Ventas POS
    df_pos = pd.read_csv(os.path.join(landing_dir, 'ventas_pos.csv'))
    df_pos['fecha'] = pd.to_datetime(df_pos['fecha']).dt.strftime('%Y-%m-%d')
    df_pos.to_parquet(os.path.join(bronze_dir, 'ventas_pos.parquet'))
    
    # Ventas Online
    df_online = pd.read_csv(os.path.join(landing_dir, 'ventas_online.csv'))
    df_online['fecha'] = pd.to_datetime(df_online['fecha']).dt.strftime('%Y-%m-%d')
    df_online.to_parquet(os.path.join(bronze_dir, 'ventas_online.parquet'))
    
    print("[KERNEL] Transformación a Bronze (Parquet) exitosa. Formatos estandarizados a ISO 8601.")

def build_silver_star_schema():
    bronze_dir = os.path.join(BASE_DIR, 'bronze')
    silver_dir = os.path.join(BASE_DIR, 'silver')
    
    df_clientes = pd.read_parquet(os.path.join(bronze_dir, 'clientes.parquet'))
    df_prod = pd.read_parquet(os.path.join(bronze_dir, 'productos.parquet'))
    df_pos = pd.read_parquet(os.path.join(bronze_dir, 'ventas_pos.parquet'))
    df_online = pd.read_parquet(os.path.join(bronze_dir, 'ventas_online.parquet'))
    
    # Dim Cliente
    dim_cliente = df_clientes.copy()
    dim_cliente.to_parquet(os.path.join(silver_dir, 'dim_cliente.parquet'))
    
    # Dim Producto
    # Inyectando registro para productos desconocidos en online sales
    unknown_prod = pd.DataFrame([{'id_producto': -1, 'nombre_producto': 'Desconocido', 'categoria': 'N/A', 'precio_base': 0, 'proveedor': 'N/A'}])
    dim_producto = pd.concat([df_prod, unknown_prod], ignore_index=True)
    dim_producto.to_parquet(os.path.join(silver_dir, 'dim_producto.parquet'))
    
    # Fact Ventas Consolidadas
    # POS -> id_venta, fecha, id_cliente, id_producto, total (cant*precio), canal='Tienda Fisica'
    fact_pos = df_pos.copy()
    fact_pos['total'] = fact_pos['cantidad'] * fact_pos['precio_unitario']
    fact_pos['canal'] = 'Tienda Fisica'
    fact_pos['id_transaccion'] = 'POS-' + fact_pos['id_venta'].astype(str)
    fact_pos = fact_pos[['id_transaccion', 'fecha', 'id_cliente', 'id_producto', 'total', 'canal']]
    
    # Online -> id_orden, fecha, id_cliente, id_producto=-1, total, canal=canal
    fact_online = df_online.copy()
    fact_online['id_producto'] = -1
    fact_online['id_transaccion'] = 'WEB-' + fact_online['id_orden'].astype(str)
    fact_online = fact_online[['id_transaccion', 'fecha', 'id_cliente', 'id_producto', 'total', 'canal']]
    
    fact_ventas = pd.concat([fact_pos, fact_online], ignore_index=True)
    
    # Validacion contra Dim Producto y Cliente
    valid_clientes = dim_cliente['id_cliente'].unique()
    valid_productos = dim_producto['id_producto'].unique()
    
    fact_ventas.loc[~fact_ventas['id_cliente'].isin(valid_clientes), 'id_cliente'] = -1 # Asumir -1 como cliente desconocido si lo hubiera
    fact_ventas.loc[~fact_ventas['id_producto'].isin(valid_productos), 'id_producto'] = -1
    
    fact_ventas.to_parquet(os.path.join(silver_dir, 'fact_ventas.parquet'))
    
    print("[KERNEL] Esquema Estrella (Silver) ensamblado. CPU desahogada tras el join.")

def generate_gold_and_analytics():
    silver_dir = os.path.join(BASE_DIR, 'silver')
    gold_dir = os.path.join(BASE_DIR, 'gold')
    
    dim_cliente = pd.read_parquet(os.path.join(silver_dir, 'dim_cliente.parquet'))
    dim_producto = pd.read_parquet(os.path.join(silver_dir, 'dim_producto.parquet'))
    fact_ventas = pd.read_parquet(os.path.join(silver_dir, 'fact_ventas.parquet'))
    
    # Enriquecimiento para Gold
    gold_df = fact_ventas.merge(dim_cliente, on='id_cliente', how='left')
    gold_df = gold_df.merge(dim_producto, on='id_producto', how='left')
    
    # Limpieza de nulos por cruces (si un cliente -1 existiera, rellenar)
    gold_df.fillna('N/A', inplace=True)
    
    dataset_path = os.path.join(gold_dir, 'dataset_retail_limpio.csv')
    gold_df.to_csv(dataset_path, index=False)
    print(f"[KERNEL] Dataset Gold exportado a: {dataset_path}")
    
    # Analiticas solicitadas
    print("\\n=== RESULTADOS DE AGREGACIÓN KPIs ===")
    
    # 1. 3 clientes con mayor volumen
    top_clientes = gold_df.groupby(['id_cliente', 'nombre', 'apellido'])['total'].sum().reset_index()
    top_clientes = top_clientes.sort_values(by='total', ascending=False).head(3)
    print("\\n[+] TOP 3 CLIENTES (LTV):")
    print(top_clientes.to_string(index=False))
    
    # 2. Rendimiento por canal
    canal_perf = gold_df.groupby('canal')['total'].sum().reset_index().sort_values(by='total', ascending=False)
    print("\\n[+] RENDIMIENTO POR CANAL:")
    print(canal_perf.to_string(index=False))
    
    # 3. Productos con mayor rotación (ignorando los 'Desconocidos' del canal online que no registran id_producto real)
    rotacion_prod = gold_df[gold_df['id_producto'] != -1].groupby(['id_producto', 'nombre_producto'])['total'].sum().reset_index()
    rotacion_prod = rotacion_prod.sort_values(by='total', ascending=False).head(3)
    print("\\n[+] TOP 3 PRODUCTOS (ROTACIÓN):")
    print(rotacion_prod.to_string(index=False))
    print("\\n[KERNEL] Consultas de agregación ejecutadas. Liberando memoria.")

if __name__ == "__main__":
    print("[SYSTEM INITIALIZATION: PANTHEON KERNEL v3.0 - H0P3 OVERRIDE]")
    setup_datalake()
    create_raw_files()
    clean_and_bronze()
    build_silver_star_schema()
    generate_gold_and_analytics()
    print("[KERNEL] Proceso ELT finalizado sin fatal traps.")
