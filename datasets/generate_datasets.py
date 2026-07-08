import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta

# Directorio base
BASE_DIR = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP/datasets"

# Semilla fija para reproducibilidad
random.seed(42)

# Tiendas y Regiones
TIENDAS = [
    {"tienda": "Santiago", "region": "Región Metropolitana", "tipo": "Express"},
    {"tienda": "Providencia", "region": "Región Metropolitana", "tipo": "Principal"},
    {"tienda": "Maipú", "region": "Región Metropolitana", "tipo": "Express"},
    {"tienda": "Las Condes", "region": "Región Metropolitana", "tipo": "Principal"},
    {"tienda": "La Florida", "region": "Región Metropolitana", "tipo": "Express"},
    {"tienda": "Puente Alto", "region": "Región Metropolitana", "tipo": "Express"},
    {"tienda": "Ñuñoa", "region": "Región Metropolitana", "tipo": "Express"},
    {"tienda": "Concepción", "region": "Región del Biobío", "tipo": "Principal"},
    {"tienda": "Valparaíso", "region": "Región de Valparaíso", "tipo": "Principal"},
    {"tienda": "Temuco", "region": "Región de la Araucanía", "tipo": "Express"}
]

# Canales
CANALES = ["web", "app"]

def generate_all_data():
    os.makedirs(BASE_DIR, exist_ok=True)

    # 1. Clientes CRM (25 registros)
    clientes_data = [
        (101, "Juan", "Pérez", "juan.perez@email.com", "Premium", "Santiago"),
        (102, "Ana", "Gómez", "ana.gomez@email.com", "Regular", "Valparaíso"),
        (103, "Carlos", "Rojas", "carlos.rojas@email.com", "Premium", "Concepción"),
        (104, "María", "López", "maria.lopez@email.com", "Nuevo", "Santiago"),
        (105, "Pedro", "Díaz", "pedro.diaz@email.com", "Regular", "Temuco"),
        (106, "Laura", "Martínez", "laura.martinez@email.com", "Premium", "Santiago"),
        (107, "Diego", "Soto", "diego.soto@email.com", "Nuevo", "Antofagasta"),
        (108, "Sofía", "Reyes", "sofia.reyes@email.com", "Regular", "Santiago"),
        (109, "Andrés", "Castro", "andres.castro@email.com", "Premium", "La Serena"),
        (110, "Camila", "Vega", "camila.vega@email.com", "Nuevo", "Santiago"),
        (111, "José", "Muñoz", "jose.munoz@email.com", "Regular", "Rancagua"),
        (112, "Francisca", "Silva", "francisca.silva@email.com", "Premium", "Viña del Mar"),
        (113, "Luis", "Pizarro", "luis.pizarro@email.com", "Regular", "Concepción"),
        (114, "Valentina", "Herrera", "valentina.herrera@email.com", "Premium", "Santiago"),
        (115, "Manuel", "Flores", "manuel.flores@email.com", "Nuevo", "Talca"),
        (116, "Constanza", "Morales", "constanza.morales@email.com", "Regular", "Santiago"),
        (117, "Javier", "Fuentes", "javier.fuentes@email.com", "Premium", "Iquique"),
        (118, "Antonia", "Valenzuela", "antonia.valenzuela@email.com", "Nuevo", "Chillán"),
        (119, "Francisco", "Araya", "francisco.araya@email.com", "Regular", "Santiago"),
        (120, "Catalina", "Carrasco", "catalina.carrasco@email.com", "Premium", "Puerto Montt"),
        (121, "Gabriel", "Alvarez", "gabriel.alvarez@email.com", "Regular", "Santiago"),
        (122, "Ignacia", "Contreras", "ignacia.contreras@email.com", "Nuevo", "Valparaíso"),
        (123, "Felipe", "Sepúlveda", "felipe.sepulveda@email.com", "Premium", "Concepción"),
        (124, "Javiera", "Muñoz", "javiera.munoz@email.com", "Regular", "Temuco"),
        (125, "Christian", "Pardo", "christian.pardo@email.com", "Premium", "Santiago")
    ]
    df_clientes = pd.DataFrame(clientes_data, columns=["id_cliente", "nombre", "apellido", "email", "segmento", "ciudad"])
    df_clientes.to_csv(os.path.join(BASE_DIR, "clientes_crm.csv"), index=False)
    print(f"[GEN] Creado clientes_crm.csv: {len(df_clientes)} registros")

    # 2. Productos ERP (18 registros)
    productos_data = [
        (2001, "Notebook Lenovo", "Tecnología", 140000, "Lenovo"),
        (2002, "Smartphone Samsung", "Tecnología", 280000, "Samsung"),
        (2003, "Polera Hombre", "Vestuario", 30000, "Nike"),
        (2004, "Silla Oficina", "Hogar", 15000, "Ikea"),
        (2005, "Audífonos Sony", "Tecnología", 70000, "Sony"),
        (2006, "Tablet Huawei", "Tecnología", 100000, "Huawei"),
        (2007, "Zapatos Mujer", "Vestuario", 50000, "Adidas"),
        (2008, "Microondas", "Hogar", 80000, "LG"),
        (2009, "Monitor", "Tecnología", 120000, "Dell"),
        (2010, "Mochila", "Vestuario", 25000, "Puma"),
        (2011, "Teclado Mecánico", "Tecnología", 35000, "HyperX"),
        (2012, "Mouse Gamer", "Tecnología", 20000, "Logitech"),
        (2013, "Mesa Escritorio", "Hogar", 45000, "Ikea"),
        (2014, "Lámpara LED", "Hogar", 12000, "Philips"),
        (2015, "Casaca Térmica", "Vestuario", 60000, "Columbia"),
        (2016, "Smartwatch Xiaomi", "Tecnología", 45000, "Xiaomi"),
        (2017, "Aspiradora Robot", "Hogar", 130000, "Eufy"),
        (2018, "Zapatillas Running", "Vestuario", 75000, "Nike")
    ]
    df_productos = pd.DataFrame(productos_data, columns=["id_producto", "nombre_producto", "categoria", "precio_base", "proveedor"])
    df_productos.to_csv(os.path.join(BASE_DIR, "productos_erp.csv"), index=False)
    print(f"[GEN] Creado productos_erp.csv: {len(df_productos)} registros")

    # Iniciar simulación de 10 días (Día 1 al Día 10)
    start_date = datetime(2026, 4, 1)
    
    total_pos_tx = 0
    total_online_tx = 0
    total_events = 0

    os.makedirs(os.path.join(BASE_DIR, "ventas_pos"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "ventas_online"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "eventos_app"), exist_ok=True)

    pos_id_counter = 1
    online_id_counter = 5001
    event_id_counter = 1

    for day in range(1, 11):
        current_date = start_date + timedelta(days=day-1)
        date_str = current_date.strftime('%Y-%m-%d')
        day_key = f"dia{day}"
        
        # --- 3. VENTAS POS (Tienda Física) ---
        # Progresión incremental: generamos 6 + (day * 2) transacciones por día
        num_pos_tx = 6 + (day * 2)
        pos_day_dir = os.path.join(BASE_DIR, "ventas_pos", day_key)
        os.makedirs(pos_day_dir, exist_ok=True)
        
        for _ in range(num_pos_tx):
            client = random.choice(clientes_data)
            prod = random.choice(productos_data)
            tienda = random.choice(TIENDAS)
            qty = random.randint(1, 3)
            
            tx_data = {
                "id_venta": [pos_id_counter],
                "fecha": [date_str],
                "id_cliente": [client[0]],
                "id_producto": [prod[0]],
                "cantidad": [qty],
                "precio_unitario": [prod[3]],
                "tienda": [tienda["tienda"]]
            }
            df_tx = pd.DataFrame(tx_data)
            df_tx.to_csv(os.path.join(pos_day_dir, f"transaccion_pos_{pos_id_counter}.csv"), index=False)
            pos_id_counter += 1
            total_pos_tx += 1
            
        # --- 4. VENTAS ONLINE (Web & App) ---
        # Generamos 5 + day transacciones online por día
        num_online_tx = 5 + day
        online_records = []
        for _ in range(num_online_tx):
            client = random.choice(clientes_data)
            prod = random.choice(productos_data)
            canal = random.choice(CANALES)
            qty = random.randint(1, 2)
            total = qty * prod[3]
            
            online_records.append({
                "id_orden": online_id_counter,
                "fecha": date_str,
                "id_cliente": client[0],
                "id_producto": prod[0],
                "total": total,
                "canal": canal
            })
            online_id_counter += 1
            total_online_tx += 1
            
        df_online = pd.DataFrame(online_records)
        df_online.to_csv(os.path.join(BASE_DIR, "ventas_online", f"{day_key}.csv"), index=False)
        
        # --- 5. EVENTOS APP (JSON) ---
        # Generamos 8 + day eventos de la app por día
        num_events = 8 + day
        event_records = []
        for _ in range(num_events):
            client = random.choice(clientes_data)
            prod = random.choice(productos_data)
            tipo_evento = random.choice(["click", "busqueda", "compra"])
            
            event_records.append({
                "id_evento": event_id_counter,
                "id_cliente": client[0],
                "tipo": tipo_evento,
                "producto": prod[0]
            })
            event_id_counter += 1
            total_events += 1
            
        with open(os.path.join(BASE_DIR, "eventos_app", f"{day_key}.json"), "w") as f:
            json.dump(event_records, f, indent=4)
            
        print(f"[GEN] Día {day} ({date_str}) generado: {num_pos_tx} POS, {num_online_tx} Online, {num_events} Eventos App")

    print(f"\n[GEN] PROCESO COMPLETADO EXCELENTEMENTE:")
    print(f"  - Total Transacciones POS (Físico): {total_pos_tx}")
    print(f"  - Total Transacciones Online: {total_online_tx}")
    print(f"  - Total Ventas (FactVentas): {total_pos_tx + total_online_tx}")
    print(f"  - Total Eventos App: {total_events}")

if __name__ == "__main__":
    generate_all_data()
