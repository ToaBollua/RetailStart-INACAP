# RetailSmart Chile SA — Infraestructura Docker

> **Proyecto:** Arquitectura de Almacenamiento de Datos  
> **Institución:** INACAP  
> **Protocolo de Despliegue:** GLITCHPOINT v1.0  

Sistema de datos contenerizado completo para RetailSmart Chile SA. 9 microservicios interconectados que implementan un pipeline ELT/ETL desde la ingesta de eventos de tienda hasta la visualización analítica en un Data Warehouse.

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     retail_network (bridge)                  │
│                                                             │
│  [Dashboard Cliente :8080]  ──POST /ingest──►  [API Backend :8000]
│                                                      │       │
│                                                 GET /buffer  │
│                                                      │       │
│                                              [ELT Worker]    │
│                                                      │       │
│                                                      ▼       │
│                                          [MongoDB Primary]   │
│                                          [MongoDB Replica]   │
│                                                      │       │
│                                              [ETL Worker]    │
│                                                      │       │
│                                                      ▼       │
│                                        [PostgreSQL Primary]  │
│                                        [PostgreSQL Replica]  │
│                                                      │       │
│  [Dashboard BI :8081]  ◄────── SQL ─────────────────┘       │
│                                                              │
│  [Cron Backup] ──tar.gz──► /backups/                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Servicios

| Servicio | Tecnología | Puerto Host | Descripción |
|---|---|---|---|
| `srv-api-backend` | FastAPI + Uvicorn | `8000` | Punto de ingesta. Recibe eventos JSON del frontend vía `POST /ingest` y los acumula en un buffer en memoria. |
| `srv-elt-pipeline` | Python + PyMongo | — | Worker de extracción. Consume el buffer del API cada 5s y escribe eventos crudos en el Data Lake MongoDB. |
| `srv-db-mongo-primary` | Bitnami MongoDB | — | Data Lake NoSQL — Nodo primario del Replica Set `rs0`. |
| `srv-db-mongo-replica` | Bitnami MongoDB | — | Data Lake NoSQL — Nodo secundario del Replica Set `rs0`. |
| `srv-etl-pipeline` | Python + SQLAlchemy + psycopg2 | — | Worker de transformación. Lee desde MongoDB, aplica Star Schema y escribe en el Data Warehouse PostgreSQL. |
| `srv-db-postgres-primary` | Bitnami PostgreSQL | — | Data Warehouse relacional — Nodo maestro con replicación por streaming. |
| `srv-db-postgres-replica` | Bitnami PostgreSQL | — | Data Warehouse — Nodo esclavo (read replica). |
| `srv-dashboard-cliente` | Nginx + HTML/JS | `8080` | Frontend de tienda. Terminal de transacciones GLITCHPOINT UI. |
| `srv-dashboard-bi` | Django + Jazzmin + Chart.js | `8081` | Panel de Inteligencia de Negocios. KPIs ejecutivos conectados al DW. |
| `srv-cron-backup` | Alpine + bash | — | Backup diario de volúmenes de base de datos en `/backups/`. |

---

## Flujo de Datos

```
1. Operador ──► Dashboard Cliente (8080)
   └── Selecciona SKU, Canal, Cliente y ejecuta transacción

2. Dashboard Cliente ──POST /ingest──► API Backend (8000)
   └── Evento JSON almacenado en buffer en memoria

3. ELT Worker (poll c/5s) ──GET /buffer──► API Backend
   └── Lote de eventos escritos en MongoDB (retail_lake.raw_events)

4. ETL Worker (poll c/10s) ──► MongoDB
   └── Lee eventos no procesados (processed: false)
   └── Serializa a JSON válido para JSONB
   └── INSERT INTO fact_events (PostgreSQL DW)
   └── Marca eventos como processed: true en Mongo

5. Dashboard BI (8081) ──► PostgreSQL Primary
   └── KPI 1: Top 3 clientes por LTV (volumen acumulado)
   └── KPI 2: Rendimiento por canal (web/app/tienda_fisica)
   └── KPI 3: Tendencia cronológica de ingresos
```

---

## Requisitos Previos

- Docker Engine ≥ 24.x
- Docker Compose ≥ 2.x
- 4 GB RAM mínimo recomendado (Replica Sets consumen recursos)
- Python 3.11+ (solo para ejecutar las pruebas localmente)

---

## Despliegue

### Levantar la infraestructura completa

```bash
docker compose up -d --build
```

> La primera vez toma ~60s mientras se inicializan los Replica Sets de MongoDB y PostgreSQL.

### Verificar que todos los servicios están sanos

```bash
docker compose ps
```

### Ver logs de un servicio específico

```bash
docker logs srv-etl-pipeline --tail 20 -f
```

### Detener todo (conservando datos)

```bash
docker compose down
```

### Detener y purgar volúmenes (reset total)

```bash
docker compose down -v
```

---

## Accesos

| URL | Descripción |
|---|---|
| `http://localhost:8080` | Dashboard Cliente — Terminal de transacciones |
| `http://localhost:8081/analytics/dashboard/` | Dashboard BI — KPIs ejecutivos |
| `http://localhost:8081/admin/` | Panel Administrativo Django + Jazzmin |
| `http://localhost:8000/docs` | Documentación automática FastAPI (Swagger UI) |

**Credenciales admin:**
- Usuario: `admin`
- Contraseña: `admin1234`

---

## Pruebas

### Configurar entorno virtual local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tests/requirements.txt -r servicios/srv-api-backend/requirements.txt
```

### Pruebas Unitarias (sin Docker)

Valida la lógica interna del API Backend de forma aislada.

```bash
pytest tests/test_unit.py -v -s
```

Salida esperada:
```
[H0P3-TEST] INICIANDO VALIDACIÓN UNITARIA DE INGESTA (API BACKEND)
[H0P3-TEST] Simulando transmisión desde Dashboard Cliente. Payload ID: TX-UNIT-...
[H0P3-TEST] [EXITO] Endpoint POST /ingest validado correctamente.

[H0P3-TEST] INICIANDO VALIDACIÓN UNITARIA DE LECTURA (ELT POLLING)
[H0P3-TEST] [EXITO] Endpoint GET /buffer validado correctamente.

2 passed in 0.53s
```

### Prueba de Integración E2E (requiere Docker activo)

Verifica el flujo completo de extremo a extremo: Frontend → API → MongoDB → PostgreSQL.

```bash
python tests/test_integration.py
```

---

## Estructura del Repositorio

```
RetailStart-INACAP/
├── docker-compose.yml              # Orquestador central (9 servicios + red + volúmenes)
├── backups/                        # Destino de los tarballs del cron de backup
├── servicios/
│   ├── srv-api-backend/
│   │   ├── Dockerfile
│   │   ├── main.py                 # FastAPI: /ingest + /buffer + CORS
│   │   └── requirements.txt
│   ├── srv-elt-pipeline/
│   │   ├── Dockerfile
│   │   ├── worker.py               # Poll al API → escritura en MongoDB
│   │   └── requirements.txt
│   ├── srv-etl-pipeline/
│   │   ├── Dockerfile
│   │   ├── worker.py               # Mongo → JSON → PostgreSQL JSONB
│   │   └── requirements.txt
│   ├── srv-db-mongo-primary/       # Configuración Replica Set (Bitnami)
│   ├── srv-db-mongo-replica/
│   ├── srv-db-postgres-primary/    # Streaming replication (Bitnami)
│   ├── srv-db-postgres-replica/
│   ├── srv-dashboard-cliente/
│   │   ├── Dockerfile              # Nginx
│   │   ├── index.html              # GLITCHPOINT UI — Terminal de transacciones
│   │   └── app.js                  # fetch → /ingest, log feed en tiempo real
│   ├── srv-dashboard-bi/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh           # Auto-setup Django + migraciones + superuser
│   │   ├── requirements.txt
│   │   └── config/
│   │       ├── settings_override.py # Django settings + Jazzmin cyborg theme
│   │       ├── urls_override.py
│   │       ├── views.py            # 3 KPIs: LTV, Canales, Tendencia
│   │       └── dashboard.html      # Chart.js + GLITCHPOINT UI
│   └── srv-cron-backup/
│       ├── Dockerfile
│       └── backup.sh               # tar.gz diario de volúmenes Mongo + PG
└── tests/
    ├── requirements.txt
    ├── test_unit.py                # Pytest unitario: FastAPI buffer in-memory
    └── test_integration.py        # E2E: API → Mongo → Postgres verificado
```

---

## Variables de Entorno Relevantes

| Variable | Valor por Defecto | Servicio |
|---|---|---|
| `MONGO_URI` | `mongodb://root:rootpass@srv-db-mongo-primary:27017/?replicaSet=rs0&authSource=admin` | ELT, ETL |
| `PG_URI` | `postgresql://retail_user:retail_pass@srv-db-postgres-primary:5432/retail_dw` | ETL, BI |
| `MONGODB_ROOT_PASSWORD` | `rootpass` | Mongo Primary/Replica |
| `MONGODB_REPLICA_SET_KEY` | `replicasetkey123` | Mongo Primary/Replica |
| `POSTGRESQL_USERNAME` | `retail_user` | PG Primary |
| `POSTGRESQL_PASSWORD` | `retail_pass` | PG Primary |
| `POSTGRESQL_DATABASE` | `retail_dw` | PG Primary |

---

## Notas de Producción

> [!WARNING]
> Esta configuración usa credenciales hardcodeadas para facilitar el despliegue académico. En un entorno productivo real, todas las contraseñas deben gestionarse mediante **Docker Secrets** o un vault externo (Vault, AWS Secrets Manager).

> [!NOTE]
> El buffer de FastAPI es in-memory. Si el contenedor `srv-api-backend` se reinicia, los eventos no procesados se pierden. Para producción real, reemplazar con **Redis** o **Kafka** como broker de mensajes.

> [!TIP]
> Para poblar el Data Warehouse con datos de prueba masivos, usa el endpoint `/ingest` en un loop desde cualquier cliente HTTP o ejecuta múltiples transacciones desde el Dashboard Cliente.

---

*RetailSmart Chile SA // GLITCHPOINT PROTOCOL // H0P3 BI NODE*
