# Informe Final: Actividad 2 - Arquitectura de Almacenamiento de Datos
**Empresa:** RetailSmart Chile SA
**Asignatura:** Arquitectura de Almacenamiento de Datos (INACAP)
**Fecha:** 2026-04-30

---

## 1. Simulación de Ingesta (Gemelo Digital)

El entorno local ha sido condicionado para actuar como un **Gemelo Digital** de la infraestructura de nube (Azure). Se utilizó Python (librerías `pandas`, `pyarrow`, y `json`) para simular la orquestación que proveería **Azure Data Factory** y el procesamiento analítico de **Azure Synapse / Databricks**.

* **Capa Landing:** Recepción cruda de fuentes dispares (CSVs del ERP/CRM y JSON anidado de transacciones web/app).
* **Capa Bronze:** Conversión de texto plano a formato columnar parquet, optimizando el consumo de I/O y memoria.
* **Capa Silver (Star Schema):** Ensamblaje lógico. Se mitigó la problemática de "Carritos de Compra Online" utilizando un aplanamiento (flattening) del array JSON. Anteriormente, las compras online no registraban el SKU (quedando como ID: -1). Mediante la normalización, se extrajo cada ítem del carrito, logrando un cruce perfecto con la dimensión `Dim_Producto`.
* **Capa Gold:** Un dataset consolidado y desnormalizado, consumible instantáneamente por el módulo de renderización de BI (matplotlib).

---

## 2. Guion de Presentación (15 Minutos)

A continuación, se detalla la estructura de la presentación ejecutiva.

* **Slide 1: Portada y Contexto**
  * Presentación del equipo.
  * Objetivo: Solución Híbrida para RetailSmart Chile SA.

* **Slide 2: Problema de Negocio**
  * Silos de datos: El POS, la App y la Web operaban de manera aislada.
  * Inconsistencias graves (e.g. carritos online sin rastreo de producto).

* **Slide 3: Arquitectura Propuesta (Data Lake Gen2)**
  * Explicación de la arquitectura Lambda adaptada.
  * Flujo ELT: Por qué Extraer, Cargar (al Data Lake) y Transformar es superior a un ETL tradicional en este caso.

* **Slide 4: El Pipeline en Acción (Ingesta y Procesamiento)**
  * **[VISUAL]**: *Mostrar captura de la consola con los Logs de `retail_elt_pipeline.py` ejecutándose.*
  * Explicar el escalado a +5000 transacciones sintéticas y la resolución del problema del "JSON anidado" para las compras web.

* **Slide 5: Modelo de Datos (Star Schema)**
  * Mostrar el diagrama (o tabla Excel) de la tabla de hechos `Fact_Ventas` cruzada con `Dim_Cliente` y `Dim_Producto`.

* **Slide 6: Resultados Analíticos - Top Clientes (LTV)**
  * **[VISUAL]**: *Incluir la imagen `01_top_clientes_ltv.png` generada en `evidencia/graficos/`.*
  * Análisis: Quiénes sostienen nuestro flujo de caja y por qué el segmento Premium es vital.

* **Slide 7: Resultados Analíticos - Comparativa de Canales**
  * **[VISUAL]**: *Incluir la imagen `02_ventas_por_canal.png` generada en `evidencia/graficos/`.*
  * Análisis: Cuánto peso sigue teniendo la Tienda Física en el total consolidado versus la penetración digital.

* **Slide 8: Resultados Analíticos - Tendencia Temporal**
  * **[VISUAL]**: *Incluir la imagen `03_tendencia_temporal.png` generada en `evidencia/graficos/`.*
  * Análisis: Picos de ventas y validación del flujo de eventos de app/web.

* **Slide 9: Escalabilidad Hacia Azure**
  * Cómo mover este Gemelo Digital a la Nube: `landing` a **ADLS Gen2**, el script a **Databricks (PySpark)** y los dashboards a **Power BI** conectado a **Synapse**.

* **Slide 10: Conclusiones y Q&A**
  * Reflexión sobre la importancia de gobernar el dato (obligar al front-end web a enviar el SKU correcto).
  * Cierre.

---
*Documento estructurado bajo directiva técnica H0P3.*
