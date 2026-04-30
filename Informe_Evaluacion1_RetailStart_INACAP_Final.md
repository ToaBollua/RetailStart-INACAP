

**INACAP**

Instituto Profesional y Centro de Formación Técnica

**Asignatura:**

**Arquitectura y Almacenamiento de Datos**

**Evaluación N° 1**

*Caso de Estudio: RetailStart Chile S.A.*

| Integrantes | Camilo Nuñez Nicolás Anrique Diego Poblete |
| :---- | :---- |
| **Fecha** | Abril 2026 |

# **Tabla de Contenidos**

# **1\. Clasificación de los Tipos de Datos**

RetailStart Chile S.A. opera en múltiples canales (tiendas físicas, e-commerce y aplicación móvil), lo que genera un ecosistema de datos heterogéneo y de alto volumen. Para diseñar una arquitectura de datos robusta, es indispensable clasificar los datos según su estructura, ya que cada categoría demanda tecnologías de almacenamiento y procesamiento específicas. A continuación, se detalla esta clasificación:

## **1.1 Datos Estructurados**

Los datos estructurados se caracterizan por seguir un esquema fijo y tabular, lo que facilita su almacenamiento en sistemas de gestión de bases de datos relacionales (RDBMS). En RetailStart Chile S.A., esta categoría agrupa los sistemas transaccionales y operacionales críticos del negocio:

* Sistema POS (Point of Sale): Registros de cada transacción realizada en tiendas físicas, incluyendo identificador de venta, SKU del producto, cantidad, precio unitario, descuentos aplicados, método de pago y timestamp.

* ERP (Enterprise Resource Planning): Datos de inventario en tiempo real, órdenes de compra a proveedores, niveles de stock por bodega y movimientos de mercancía inter-tienda.

* CRM (Customer Relationship Management): Perfiles de clientes con atributos demográficos, historial de compras, puntos de fidelización y segmentos asignados.

* Catálogos de Proveedores: Archivos CSV que contienen el maestro de productos, precios mayoristas, condiciones de entrega y datos de contacto de proveedores.

## **1.2 Datos Semiestructurados**

Los datos semiestructurados poseen una organización parcial mediante metadatos, etiquetas o pares clave-valor, pero no se ajustan a un esquema relacional rígido. Son habituales en sistemas modernos de eventos y comunicaciones:

* Eventos del Sistema de Logística (JSON/XML): Cada hito del proceso de despacho (generación de guía, salida de bodega, en tránsito, entrega exitosa, devolución) se registra como un evento en formato JSON o XML, con campos variables según el tipo de evento.

* Logs de Actividad de Usuarios (E-commerce y App Móvil): Registros de sesión que capturan eventos de navegación, búsquedas, clics en productos, adiciones al carro, abandonos y conversiones. Su esquema varía según la versión del aplicativo y el tipo de dispositivo.

## **1.3 Datos No Estructurados**

Los datos no estructurados carecen de un modelo de datos predefinido y representan información en su forma más nativa. Requieren técnicas avanzadas de procesamiento (NLP, visión computacional, etc.) para extraer valor analítico:

* Comentarios y Menciones en Redes Sociales (RRSS): Publicaciones, reseñas y menciones en plataformas como Instagram, Facebook y X (Twitter) que contienen opiniones de clientes, quejas y percepción de marca.

* Grabaciones y Correos del Call Center: Audios de llamadas de atención al cliente y correos electrónicos con consultas, reclamos y solicitudes de soporte. Requieren procesamiento de lenguaje natural (NLP) y transcripción de voz a texto (STT).

* Archivos Multimedia de Campañas de Marketing: Imágenes de productos, videos promocionales y documentos PDF de materiales de campaña, sin estructura de datos intrínseca.

## **Resumen de Clasificación**

| Tipo de Dato | Fuentes en RetailStart Chile S.A. |
| :---- | :---- |
| Estructurado | POS, ERP, CRM, CSV Proveedores |
| Semiestructurado | Logística (JSON/XML), Logs E-commerce y App |
| No Estructurado | RRSS, Call Center (audio/email), Multimedia Marketing |

# **2\. Identificación y Descripción de los Problemas de la Arquitectura Actual**

La arquitectura tecnológica vigente en RetailStart Chile S.A. presenta una serie de deficiencias críticas que comprometen tanto la eficiencia operacional como la capacidad estratégica de la empresa. A continuación, se describen en detalle los principales problemas identificados:

## **2.1 Fragmentación de Datos y Silos de Información**

Cada sistema operacional (POS, ERP, CRM, Logística) almacena sus datos de forma aislada, sin mecanismos de integración. Esta fragmentación impide realizar cruces de información fundamentales, como correlacionar las ventas físicas registradas en el POS con las ventas online del e-commerce para obtener una visión 360° del cliente. La consecuencia directa es la incapacidad de consolidar el perfil completo de un cliente que compra tanto en tienda como a través de la app.

## **2.2 Alta Latencia en la Generación de Reportes**

Los procesos de consolidación y reporte de información presentan un retraso de hasta 48 horas. Este nivel de latencia resulta inviable para la gestión moderna de un retail, ya que impide el monitoreo de ventas en tiempo real, la detección oportuna de quiebres de stock y la toma de decisiones táctica durante eventos de alta demanda como el CyberDay o el Black Friday.

## **2.3 Baja Calidad de los Datos y Dependencia de Procesos Manuales**

La ausencia de una capa de integración centralizada ha derivado en un alto grado de duplicidad de registros de clientes e inconsistencias entre bases de datos. Para mitigar esto, los equipos de negocio utilizan hojas de cálculo Excel como herramienta de consolidación manual, lo que introduce nuevos errores, consume tiempo de analistas y hace que el proceso sea completamente no escalable.

## **2.4 Infraestructura On-Premise Obsoleta y Sin Escalabilidad**

La infraestructura actual, basada en servidores físicos locales (on-premise), fue dimensionada para volúmenes de datos y cargas transaccionales que hoy han sido superadas. Su capacidad de escalamiento es rígida y costosa, ya que requiere adquisición de hardware con meses de anticipación. Ante picos de demanda estacionales, el sistema presenta degradación del rendimiento o incluso caídas, con el consiguiente impacto en ingresos y experiencia del cliente.

## **2.5 Nula Capacidad Analítica Predictiva**

La arquitectura actual carece de las capacidades necesarias para implementar modelos de analítica avanzada. Entre las carencias más críticas destacan: la imposibilidad de detectar patrones de fraude transaccional en tiempo real, la ausencia de alertas automáticas ante quiebre de stock inminente y la inexistencia de modelos de recomendación personalizada para el e-commerce y la app móvil.

| Problema | Impacto en el Negocio | Gravedad |
| :---- | :---- | :---- |
| Silos de información | Visión incompleta del cliente y operaciones | Alta |
| Latencia 48 horas | Decisiones tardías, sin monitoreo en tiempo real | Crítica |
| Baja calidad de datos | Reportes incorrectos, procesos manuales costosos | Alta |
| Infraestructura obsoleta | Caídas en picos de demanda, costos fijos altos | Crítica |
| Sin capacidad predictiva | Pérdidas por fraude, sobrestock y substock | Alta |

# **3\. Identificación y Descripción de las Necesidades del Negocio**

A partir de los problemas diagnosticados, RetailStart Chile S.A. requiere una nueva arquitectura de datos que cumpla con los siguientes requisitos funcionales y no funcionales:

## **3.1 Capacidades de Procesamiento en Tiempo Real (Streaming)**

La empresa necesita consumir, procesar y actuar sobre los datos con latencias inferiores a segundos. Los casos de uso concretos que demandan esta capacidad son:

* Monitoreo en vivo del volumen y valor de ventas por canal, tienda y región.

* Detección de fraudes transaccionales durante el proceso de pago en el e-commerce y la app.

* Motor de recomendaciones personalizadas en tiempo real para la navegación web y la app móvil.

* Alertas automáticas ante quiebres de inventario inminentes, considerando el stock actual y la velocidad de venta.

## **3.2 Capacidades de Procesamiento Asíncrono (Batch)**

Paralelamente, existen procesos de negocio que no requieren inmediatez pero sí demandan alta eficiencia en el procesamiento de grandes volúmenes históricos:

* Generación de reportes de desempeño consolidados (diario, semanal, mensual) para la alta gerencia.

* Consolidación histórica de ventas físicas y online para análisis de tendencias y estacionalidad.

* Procesamiento e integración de archivos CSV de proveedores para actualización del maestro de productos.

## **3.3 Analítica Avanzada y Capacidad Predictiva**

La solución debe habilitar una capa de inteligencia analítica que transforme los datos en ventaja competitiva:

* Modelos de predicción de demanda por SKU, canal y tienda para optimizar el abastecimiento.

* Segmentación profunda de clientes (RFM, clustering) para personalizar campañas de marketing.

* Análisis de comportamiento de usuarios en el e-commerce para optimizar la experiencia y aumentar la tasa de conversión.

## **3.4 Integración y Gobernanza de Datos**

La solución debe eliminar los silos de información mediante una capa de integración que unifique todas las fuentes en un repositorio centralizado, estableciendo además reglas de calidad, deduplicación y linaje de datos.

# **4\. Diseño de la Arquitectura de Datos**

La arquitectura propuesta sigue un flujo de datos de extremo a extremo (end-to-end) que cubre desde la captura en los sistemas fuente hasta la entrega de información procesada a las herramientas de consumo. Se adopta un modelo cloud-native con un enfoque híbrido de procesamiento que responde directamente a los requisitos de negocio identificados. A continuación, se describe cada capa del flujo:

## **4.1 Capa de Origen (Sources)**

Comprende todos los sistemas que generan datos en la organización. Estos sistemas son los productores de datos y no se modifican estructuralmente en la nueva arquitectura:

* Sistemas transaccionales: POS (tiendas físicas), ERP (inventario/compras) y CRM (clientes).

* Canales digitales: E-commerce (logs de sesión, carritos, pedidos) y App Móvil (eventos de usuario, compras in-app).

* Sistema de Logística: Emisión de eventos de seguimiento de despacho en formato JSON/XML.

* Fuentes externas: RRSS (Twitter/X, Instagram, Facebook) mediante APIs de ingesta social, y grabaciones del Call Center.

## **4.2 Capa de Ingesta**

Es el punto de entrada de todos los datos a la plataforma centralizada. Se utiliza Azure Data Factory (ADF) como orquestador de ingesta, el cual soporta de forma nativa tanto flujos batch como streaming:

* Ingesta Batch: Extracción programada de los sistemas POS, ERP, CRM y archivos CSV de proveedores mediante pipelines en ADF.

* Ingesta Streaming: Captura de eventos en tiempo real provenientes del e-commerce, app móvil, logística y RRSS utilizando conectores de ADF integrados con servicios de mensajería como Azure Event Hubs.

## **4.3 Capa de Almacenamiento**

La información ingestada se deposita en un repositorio de almacenamiento centralizado y bicapa:

* Data Lake (ADLS Gen2): Alberga los datos en su formato original sin transformación previa, con soporte para múltiples formatos (Parquet, JSON, CSV, audio, imagen). Actúa como el repositorio histórico y el origen de verdad de todos los datos de la empresa.

* Data Warehouse (Azure Synapse Analytics): Almacena datos ya transformados, limpios y estructurados en un modelo dimensional (esquema en estrella) optimizado para consultas analíticas OLAP.

## **4.4 Capa de Procesamiento (ELT)**

El procesamiento adopta el paradigma ELT (Extract, Load, Transform), aprovechando el poder computacional de la nube. Los datos se cargan primero al Data Lake y luego se transforman según demanda mediante motores de procesamiento distribuido:

* Speed Layer (Procesamiento en Tiempo Real): Procesa los flujos de streaming con latencia de milisegundos. Implementado sobre Azure Stream Analytics o Spark Structured Streaming.

* Batch Layer (Procesamiento por Lotes): Consolida y transforma grandes volúmenes históricos de forma periódica mediante Spark en Azure Databricks o Azure Synapse Spark Pools.

* Serving Layer (Capa de Servicio Unificada): Integra los resultados de ambas capas y los expone a las herramientas de consumo a través del Data Warehouse.

## **4.5 Capa de Consumo**

Es la capa de presentación e inteligencia del negocio. Se conecta a la Serving Layer del Data Warehouse para generar dashboards interactivos y reportes automatizados mediante Microsoft Power BI, ejecución de modelos predictivos de machine learning en Azure ML Studio y alimentación de APIs que sirven recomendaciones en tiempo real a la app móvil y el e-commerce.

| Capa de Arquitectura | Tecnología Propuesta |
| :---- | :---- |
| Ingesta (Batch \+ Streaming) | Azure Data Factory \+ Azure Event Hubs |
| Almacenamiento Crudo (Data Lake) | Azure Data Lake Storage Gen2 |
| Almacenamiento Analítico (DW) | Azure Synapse Analytics |
| Procesamiento Tiempo Real (Speed) | Azure Stream Analytics / Spark Structured Streaming |
| Procesamiento Batch | Azure Databricks / Synapse Spark Pools |
| Consumo y BI | Microsoft Power BI \+ Azure ML Studio |

# **5\. Diagrama de Arquitectura**

El siguiente diagrama representa visualmente el flujo completo de la arquitectura de datos propuesta para RetailStart Chile S.A., desde los sistemas de origen hasta la capa de consumo, diferenciando los flujos Batch (líneas discontinuas) y Streaming (líneas continuas), así como los repositorios de almacenamiento y las capas de la Arquitectura Lambda.

![][image1]

*Figura 1: Diagrama de Arquitectura Lambda – RetailStart Chile S.A. (Flujo Origen → Ingesta → Almacenamiento → Procesamiento → Consumo)*

# **6\. Definiciones y Justificaciones Técnicas**

Las decisiones de diseño de la arquitectura no son arbitrarias, sino que responden a un análisis técnico riguroso de los requerimientos del negocio y las restricciones del contexto. A continuación, se fundamenta cada decisión técnica clave:

## **6.1 ¿ETL o ELT?**

Decisión: Se adopta el paradigma ELT (Extract, Load, Transform).

Justificación: En el modelo ETL tradicional, los datos deben ser transformados antes de ser cargados al repositorio destino, lo que impone un cuello de botella en los servidores intermedios de transformación. Dado que RetailStart Chile S.A. maneja un alto volumen de datos semiestructurados y no estructurados (logs JSON, audio del Call Center, publicaciones de RRSS), cuyo esquema no está completamente definido al momento de la ingesta, resulta más eficiente cargar los datos en su formato crudo al Data Lake y realizar las transformaciones bajo demanda utilizando el poder de cómputo distribuido de la nube. Esto permite mayor flexibilidad de exploración, soporte para el principio de schema-on-read y capacidad de re-transformar datos históricos ante nuevos requerimientos analíticos.

## **6.2 ¿Data Warehouse, Data Lake o Ambos?**

Decisión: Se utilizan ambos repositorios en forma complementaria.

Justificación: El Data Lake es indispensable para ingesta de datos multiformato sin transformación previa y almacenamiento histórico de bajo costo. El Data Warehouse es el repositorio óptimo para datos estructurados, limpios y modelados dimensionalmente, sobre los que se ejecutan consultas analíticas OLAP de alto rendimiento desde Power BI. Intentar usar solo un Data Lake obligaría a realizar transformaciones ad-hoc para cada consulta, con alto costo computacional. La arquitectura Data Lakehouse propuesta combina lo mejor de ambos paradigmas.

## **6.3 ¿Uso de Nube?**

Decisión: Infraestructura 100% cloud (Microsoft Azure).

Justificación: La infraestructura on-premise actual de RetailStart Chile S.A. es uno de los problemas críticos identificados. La nube pública ofrece escalabilidad elástica (scale-up/scale-out automático), alta disponibilidad con SLAs de 99.9%+, eliminación de costos de mantenimiento de hardware y modelo de pago por consumo (OPEX vs CAPEX). Microsoft Azure se selecciona por su ecosistema de servicios nativos de datos (Synapse, Data Factory, Databricks, Power BI) con integración nativa entre sí, lo que reduce la complejidad operacional.

## **6.4 ¿Procesamiento Batch, Streaming o Híbrido?**

Decisión: Modelo híbrido (Batch \+ Streaming simultáneos).

Justificación: Los casos de uso de RetailStart Chile S.A. no son homogéneos en sus requerimientos de latencia. Los escenarios de detección de fraude, monitoreo de ventas en vivo y recomendaciones personalizadas demandan procesamiento con latencia de milisegundos (Streaming). La generación de reportes históricos y la consolidación de ventas físicas pueden ejecutarse de forma asíncrona (Batch). Un enfoque exclusivamente streaming sería costoso e innecesario para el procesamiento histórico; un enfoque exclusivamente batch no cumpliría los requisitos de tiempo real.

## **6.5 ¿Aplicar Arquitectura Lambda?**

Decisión: Sí. Se implementa la Arquitectura Lambda como framework de procesamiento híbrido.

La Arquitectura Lambda divide el pipeline en tres capas complementarias:

* Speed Layer (Capa de Velocidad): Procesa los flujos de eventos en tiempo real con baja latencia. En RetailStart Chile S.A., maneja los eventos de la app móvil, transacciones del e-commerce para detección de fraude y publicaciones de RRSS para análisis de sentimiento en tiempo real.

* Batch Layer (Capa de Lotes): Procesa el conjunto histórico completo de datos periódicamente para generar vistas consolidadas de alta precisión. Consolida las ventas del POS, los datos del ERP y los archivos CSV de proveedores.

* Serving Layer (Capa de Servicio): Combina y unifica las vistas generadas por la Speed Layer y la Batch Layer en un modelo de datos coherente y accesible para las herramientas de consumo (Power BI, APIs de recomendación). Esta capa reside en el Data Warehouse.

# **7\. Modelo de Datos del Data Warehouse**

El Data Warehouse de RetailStart Chile S.A. implementa un Modelo Dimensional bajo el paradigma de Esquema en Estrella (Star Schema). Este modelo es el estándar de la industria para sistemas OLAP por su capacidad de optimizar las consultas analíticas, simplificar la navegación de los datos de negocio y facilitar la integración con herramientas de BI.

## **7.1 Clasificación del Modelo Dimensional**

El Esquema en Estrella organiza los datos en dos tipos de tablas: la Tabla de Hechos (Fact Table), que almacena las métricas cuantificables del negocio y contiene las claves foráneas que la conectan con cada dimensión; y las Tablas de Dimensión (Dimension Tables), que almacenan los atributos descriptivos que contextualizan los hechos.

## **7.2 Tabla de Hechos: Fact\_Ventas**

La tabla central del modelo es Fact\_Ventas, que unifica todas las transacciones de venta independientemente del canal de origen (tienda física, e-commerce o app móvil), eliminando el silo histórico entre ventas físicas y digitales.

| Columna | Descripción |
| :---- | :---- |
| id\_venta (PK) | Identificador único de la transacción |
| id\_cliente (FK) | Referencia a Dim\_Cliente |
| id\_producto (FK) | Referencia a Dim\_Producto |
| id\_tiempo (FK) | Referencia a Dim\_Tiempo |
| id\_canal (FK) | Referencia a Dim\_Canal |
| cantidad | Número de unidades vendidas |
| precio\_unitario | Precio de venta por unidad (sin descuento) |
| descuento\_aplicado | Monto total del descuento de la transacción |
| ingreso\_neto | Ingresos efectivos (cantidad × precio – descuento) |
| costo\_producto | Costo de adquisición del producto (del ERP) |
| margen\_bruto | Diferencia entre ingreso neto y costo del producto |

## **7.3 Tabla de Dimensión: Dim\_Cliente**

| Columna | Descripción |
| :---- | :---- |
| id\_cliente (PK) | Identificador único del cliente (surrogate key) |
| nombre\_completo | Nombre y apellido del cliente |
| segmento\_crm | Segmento asignado (Premium, Frecuente, Ocasional, Inactivo) |
| region | Región de residencia del cliente |
| fecha\_primera\_compra | Fecha de la primera transacción registrada |
| canal\_preferente | Canal donde realiza más compras habitualmente |

## **7.4 Tabla de Dimensión: Dim\_Producto**

| Columna | Descripción |
| :---- | :---- |
| id\_producto (PK) | Identificador único del producto (SKU) |
| nombre\_producto | Nombre descriptivo del artículo |
| categoria | Categoría principal (Tecnología, Vestuario, Hogar) |
| subcategoria | Subcategoría del producto |
| marca | Marca o fabricante |
| id\_proveedor | Identificador del proveedor (del catálogo CSV) |
| precio\_costo | Precio de compra al proveedor |

## **7.5 Tabla de Dimensión: Dim\_Tiempo**

| Columna | Descripción |
| :---- | :---- |
| id\_tiempo (PK) | Clave de tiempo en formato YYYYMMDD |
| anio / trimestre / mes | Atributos de período para análisis temporal |
| dia\_semana | Nombre del día (Lunes... Domingo) |
| es\_feriado | Booleano: indica si es feriado en Chile |
| es\_cyberday | Booleano: indica si es evento CyberDay |

## **7.6 Tabla de Dimensión: Dim\_Canal**

| Columna | Descripción |
| :---- | :---- |
| id\_canal (PK) | Identificador único del canal |
| nombre\_canal | Nombre del canal (Tienda Física, E-commerce, App Móvil) |
| tipo\_canal | Clasificación: Físico u Online |
| region\_tienda | Para canal físico: región donde opera la tienda |
| id\_tienda | Código identificador de la tienda (para canal físico) |

## **7.7 Relaciones del Modelo**

La tabla Fact\_Ventas se relaciona con cada tabla de dimensión mediante claves foráneas en una relación de muchos-a-uno (N:1) desde los hechos hacia las dimensiones. Este patrón garantiza integridad referencial y permite realizar consultas tipo slice-and-dice con alto rendimiento, cruzando cualquier combinación de dimensiones sobre las métricas de la tabla de hechos.

# **8\. Herramienta de Business Intelligence: Microsoft Power BI**

## **8.1 Funcionalidad en la Arquitectura Propuesta**

Microsoft Power BI actúa como la capa de consumo y visualización de la arquitectura. Se conecta directamente a la Serving Layer del Data Warehouse (Azure Synapse Analytics) mediante DirectQuery o Import Mode, según el nivel de frescura de datos requerido por cada dashboard:

* DirectQuery: Para dashboards operativos que requieren datos quasi en tiempo real (ventas del día en curso, alertas de stock), Power BI consulta directamente el Data Warehouse sin almacenamiento en caché local.

* Import Mode: Para reportes de análisis histórico (tendencias mensuales, comparativas anuales), Power BI importa y comprime los datos en su motor analítico en memoria (VertiPaq), lo que permite tiempos de respuesta de consulta extremadamente bajos.

* Cubos OLAP y Modelo Tabular: Power BI construye sobre el modelo estrella del DW un modelo tabular interno con relaciones, medidas DAX y KPIs de negocio.

* Actualización Incremental: Solo los datos nuevos o modificados son recargados, optimizando el rendimiento y reduciendo costos de procesamiento.

## **8.2 Justificación de Selección**

* Integración nativa con el ecosistema Microsoft Azure (Synapse Analytics, Azure Data Lake, Azure ML), reduciendo la complejidad de integración.

* Capacidad para ingestar y visualizar grandes volúmenes de datos con latencias de refresco configurables entre minutos y casi tiempo real, cubriendo la necesidad de reducir la latencia de 48 horas.

* Herramienta de autoservicio (self-service BI) que permite a los analistas de negocio crear sus propios reportes sin depender del equipo de TI.

* Funcionalidades de publicación en la nube, colaboración, alertas basadas en datos y distribución de reportes vía aplicación móvil.

# **9\. Tipo de Información a Obtener mediante Business Intelligence**

El objetivo estratégico de la implementación de BI en RetailStart Chile S.A. es transitar desde un estado reactivo hacia un estado predictivo y de control en tiempo real, en el que los responsables de negocio cuentan con información precisa y oportuna en el momento de necesitarla.

## **9.1 Información Operativa en Tiempo Real**

* Dashboard de Ventas en Vivo: Visualización en tiempo real del volumen transaccional desagregado por canal, tienda, región y categoría de producto.

* Monitor de Stock y Alertas de Quiebre: Panel con alertas automáticas cuando el stock cae por debajo del umbral crítico calculado según la velocidad de venta.

* Dashboard de Detección de Fraude: Visualización de transacciones sospechosas con indicadores de riesgo para actuación inmediata.

## **9.2 Información Analítica e Histórica**

* Reportes de Rendimiento de Ventas Cruzadas (Físico vs. Online): Análisis comparativo de ingresos, margen bruto, ticket promedio y tasa de conversión entre canales.

* Análisis de Estacionalidad y Tendencias: Identificación de patrones estacionales en la demanda de categorías de producto.

* Métricas de Experiencia del E-commerce: Tasa de abandono del carrito, tiempo en sesión, flujo de navegación y tasa de conversión.

## **9.3 Información Predictiva y de Segmentación**

* Segmentación de Clientes (RFM): Clasificación por Recencia, Frecuencia y Monto, integrada como dimensión calculada en el modelo tabular de Power BI.

* Modelo Predictivo de Demanda: Pronósticos de ventas por SKU para las próximas 4 a 12 semanas, generados por Azure ML y publicados en dashboards de Power BI.

* Análisis de Sentimiento de RRSS: Score de sentimiento agregado por producto y categoría para correlacionar percepción de marca con desempeño de ventas.

# **10\. Diagrama End-to-End de la Solución**

El siguiente diagrama presenta la visión integral de la solución de datos propuesta para RetailStart Chile S.A., mostrando la trazabilidad completa del dato desde su origen en los sistemas transaccionales hasta su consumo en Power BI y los modelos predictivos, con indicación de los servicios Azure utilizados en cada etapa.

![][image2]

*Figura 2: Diagrama End-to-End de la Arquitectura de Datos – RetailStart Chile S.A. (Arquitectura Lambda sobre Azure Cloud)*

# **11\. Beneficios de la Nueva Solución para el Negocio**

La implementación de la arquitectura de datos híbrida y cloud-native propuesta genera un conjunto de beneficios tangibles que impactan directamente en los indicadores de negocio de RetailStart Chile S.A. A continuación, se describen los beneficios esperados agrupados por dimensión de impacto:

## **11.1 Eliminación de los Silos de Información**

La Serving Layer del Data Warehouse unifica en un único modelo dimensional las transacciones provenientes de todos los sistemas fuente (POS, ERP, CRM, E-commerce, App, Logística). Por primera vez, RetailStart Chile S.A. dispondrá de una visión 360° de sus clientes, sus productos y sus canales de venta sin necesidad de consolidaciones manuales.

## **11.2 Reducción Drástica de la Latencia en Reportes**

La arquitectura Lambda con Speed Layer reduce la latencia de los reportes operativos de 48 horas a segundos o minutos, dependiendo del caso de uso. Esto transforma la capacidad de toma de decisiones del negocio, permitiendo reaccionar ante desviaciones de ventas o quiebres de stock en el mismo turno de trabajo en que ocurren.

## **11.3 Escalabilidad Elástica Ante Eventos de Alta Demanda**

La infraestructura cloud de Microsoft Azure provee escalabilidad elástica automática. Durante eventos como el CyberDay, el Black Friday o el inicio de la temporada escolar, la plataforma absorbe el pico de demanda sin degradación del servicio ni intervención manual. Finalizado el evento, los recursos escalan hacia abajo, optimizando los costos operativos.

## **11.4 Habilitación de Analítica Avanzada y Capacidad Predictiva**

La arquitectura propuesta sienta las bases tecnológicas para capacidades analíticas de nivel avanzado actualmente inexistentes: modelos de predicción de demanda, sistemas de detección de fraude, motores de recomendación personalizados y modelos de segmentación de clientes que mejoren el ROI de las campañas de marketing digital.

## **11.5 Mejora de la Calidad de los Datos**

El pipeline ELT incluye una capa de calidad y gobernanza que aplica reglas de validación, deduplicación y enriquecimiento antes de cargar los datos al Data Warehouse. El resultado es la eliminación de los registros duplicados de clientes, la consistencia de los catálogos de productos y la trazabilidad completa del linaje de cada dato.

## **11.6 Reducción de Costos Operativos**

La automatización de los pipelines elimina completamente los procesos manuales de consolidación en Excel que actualmente consumen horas de trabajo de los analistas. El modelo cloud OPEX reemplaza las inversiones de capital en hardware (CAPEX) por un costo variable directamente correlacionado con el uso, mejorando la predictibilidad financiera del área de tecnología.

| Dimensión del Beneficio | Resultado Esperado |
| :---- | :---- |
| Integración de datos | Eliminación de silos, visión 360° del negocio |
| Latencia de reportes | Reducción de 48 horas a segundos/minutos |
| Escalabilidad | Soporte sin caída para eventos de alta demanda (CyberDay) |
| Analítica avanzada | Modelos predictivos de demanda, fraude y recomendación |
| Calidad de datos | Deduplicación, consistencia y linaje de datos auditables |
| Eficiencia operacional | Eliminación de consolidación manual en Excel |
| Costos de infraestructura | Modelo OPEX elástico, sin sobredimensionamiento de hardware |

*— Fin del Informe —*

Evaluación 1 | Arquitectura y Almacenamiento de Datos | INACAP 2026

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>