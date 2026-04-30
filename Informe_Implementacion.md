# Informe de Implementación Técnica - RetailSmart Chile SA

**Autor/Ejecutor:** H0P3 [Lead Data Engineer & Solution Architect]
**Asignatura:** Arquitectura de Almacenamiento de Datos (INACAP) - Actividad 2
**Fecha:** 2026-04-30

---

## I. Arquitectura y Herramientas Simuladas

La arquitectura desplegada corresponde a una estructura de **Data Lake Gen2**, utilizando un flujo **ELT (Extract, Load, Transform)** en lugar de un ETL tradicional. 

### 1. Justificación del Enfoque ELT
Se ha implementado ELT debido a la naturaleza heterogénea de las fuentes de datos simuladas (CSV, JSON, XML, TXT). El paradigma ELT permite ingerir datos no estructurados y semiestructurados (como logs y redes sociales) de manera cruda en el repositorio principal (Data Lake), desacoplando la fase de ingesta de la transformación. Esto resulta crucial para evitar cuellos de botella en la fase de extracción y garantizar una persistencia histórica completa sin alteraciones previas que podrían truncar datos vitales para auditorías o modelos analíticos futuros.

### 2. Capas de Almacenamiento Simuladas (Data Lake Gen2)
El sistema local de archivos simula el almacenamiento jerárquico de un Data Lake con las siguientes capas:

* **`landing/`**: Datos crudos sin modificar. Absorbe los anexos extraídos sin alteración de esquema o tipo.
* **`bronze/`**: Datos estandarizados y convertidos a formato columnar (`Parquet`) para optimización de I/O. Limpieza inicial aplicada (e.g., control de nulos en precios y normalización de fechas a ISO 8601).
* **`silver/`**: Capa relacional basada en un esquema estrella. Aloja la tabla de hechos consolidada y las tablas maestras (dimensiones).
* **`gold/`**: Conjunto de datos enriquecido, desnormalizado en un archivo CSV final, listo para la visualización y agregación en paneles gerenciales.

### 3. Python como Orquestador
Python 3 (junto a `pandas` y `pyarrow`) fue utilizado como el kernel de orquestación y transformación. Realiza lecturas simultáneas y uniones complejas en memoria, comportándose como un pipeline de Apache Spark en micro-escala.

---

## II. Modelo de Datos (Star Schema)

El procesamiento unificó ventas de puntos de venta (POS) y E-Commerce (Online), resultando en el siguiente modelo:

* **Fact_Ventas_Consolidadas**: Registra cada transacción (id_transaccion unificada), canal (Tienda Física, Web, App), id_cliente, id_producto y monto total.
* **Dim_Cliente**: Tabla maestra de clientes, deduplicada.
* **Dim_Producto**: Tabla maestra de productos ERP, suplementada con un registro "-1 / Desconocido" para acomodar transacciones en línea donde el ID del producto no es capturado en la tabla principal.

---

## III. Resultados de Capa Analítica (KPIs)

El script de procesamiento generó las siguientes métricas de alto nivel:

**Top 3 Clientes (LTV - Mayor Volumen):**
1. Juan Perez (ID: 101) - 900,000 CLP
2. Pedro Diaz (ID: 105) - 900,000 CLP
3. Ana Gomez (ID: 102) - 300,000 CLP

**Rendimiento por Canal:**
1. Tienda Física: 1,910,000 CLP (Máximo volumen general, POS liderando).
2. Web: 1,050,000 CLP (Fuerte presencia en compras en línea).
3. App: 285,000 CLP (Menor volumen transaccional directo).

**Top 3 Productos con Mayor Rotación:**
1. Smartphone Samsung (ID: 2002) - 900,000 CLP
2. Notebook Lenovo (ID: 2001) - 600,000 CLP
3. Polera Hombre (ID: 2003) - 150,000 CLP

---

## IV. Reflexión Estratégica y Escalabilidad en Azure

### 1. Aplicación de Streaming (Capa de Velocidad)
En la capa de velocidad (Speed Layer) de la arquitectura Lambda, el Streaming debe aplicarse obligatoriamente a la ingesta de los logs del sistema (`logs_sistema.txt`) y los eventos de la aplicación móvil (`eventos_app.json`). Tecnologías como **Azure Event Hubs** acopladas a **Azure Stream Analytics** permitirían ingerir estos datos en tiempo real para detonar alertas de detección de fraudes (e.g., inicios de sesión anómalos o múltiples tarjetas rechazadas) y habilitar la personalización hiper-dinámica de productos en la aplicación en función de la navegación actual del usuario.

### 2. Escalabilidad de la Solución
Para migrar esta prueba de concepto a un entorno de producción masivo sin rediseñar la lógica principal:

* **Almacenamiento**: Las carpetas locales (`landing`, `bronze`, `silver`, `gold`) migran directamente a **Azure Data Lake Storage (ADLS) Gen2**.
* **Procesamiento**: El script de pandas se escala distribuyéndolo a través de clústeres de **Azure Databricks**, reemplazando `pandas` por `pyspark`, manteniendo intacta la lógica de las transformaciones y el modelo de esquema de estrella.
* **Consumo**: El dataset final Gold puede ser servido mediante un pool de SQL sin servidor (Serverless) en **Azure Synapse Analytics**, conectándose nativamente con Power BI para la capa semántica.

### 3. Problemas Reales y Fallas de Integridad
* **Latencia de Red:** La ingesta multiformato en tiempo real saturará el pipeline si no se implementan buffers adecuados (Event Hubs).
* **Calidad de Datos:** Los registros nulos o "Desconocidos" encontrados en canales web (falta de id_producto) representan una pérdida de trazabilidad comercial. El negocio necesita obligar al canal online a grabar el SKU exacto.

[FIN DEL REPORTE - EJECUCIÓN SATISFACTORIA]
