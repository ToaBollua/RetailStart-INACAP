

| Evaluación Nro.: 1  Arquitectura y Almacenamiento de Datos  |  |
| ----- | :---- |
| Carrera: Analista Programador/Ingeniería en Informática |  |
| Asignatura:  Arquitectura y Almacenamiento de Datos |  |
| Nombre Docente: Juan Paredes Sanhueza |  |
|  |  |
| Código Asignatura/Sección: TI3051-D-IEI-N5-P2-C1 | Fecha: 16-04-2026 |
| Nombre Estudiante : | Rut: |
| Puntaje Obtenido: | Nota : |
| Puntaje por Ítem y/o Pregunta:     Las actividades se evaluarán en base a instrumento de evaluación “rúbrica”, la cual contiene los puntajes de los ítem a evaluar.  **TOTAL DE PUNTOS EVALUACIÓN**: 100 **PUNTAJE MÍNIMO (Nota 4,0):**  60 puntos (60 %) |  |
| **Instrucciones:**   Realizar el trabajo en forma grupal o individual en base a actividades planteadas |  |

Taller

La empresa **RetailStart Chile S.A.** es una cadena de retail con presencia a nivel nacional que comercializa productos de tecnología, vestuario y hogar a través de:

* Tiendas físicas en todo Chile   
* Plataforma e-commerce   
* Aplicación móvil 

Durante los últimos años, la empresa ha crecido rápidamente, incorporando distintos sistemas tecnológicos sin una estrategia de integración de datos.

**Fuentes de Datos:**

La empresa cuenta con las siguientes fuentes de información:

* **Sistema POS (puntos de venta en tiendas físicas)**  
  Registra cada transacción de venta con información como producto, cantidad, precio, fecha y cliente.   
* **Sistema ERP**  
  Gestiona inventario, compras a proveedores y datos financieros de la empresa.   
* **Sistema CRM**  
  Contiene información de clientes, historial de compras y segmentación de marketing.   
* **Plataforma E-commerce**  
  Genera información de compras online y navegación de usuarios.  
* **Aplicación móvil**  
  Registra eventos de uso como clics, búsquedas y tiempo de navegación.  
* **Sistema de logística**  
  Permite hacer seguimiento de pedidos y estados de entrega mediante servicios que entregan información en formatos como JSON o XML.   
* **Logs de sistemas**  
  Registros de actividad de usuarios y sistemas.  
* **Redes sociales**  
  Comentarios, reseñas y menciones de clientes sobre productos y servicios.   
* **Call center / atención al cliente**  
  Grabaciones de llamadas, correos electrónicos y chats con clientes.   
* **Archivos de proveedores**  
  Información de productos, precios y catálogos entregados en formatos como CSV, PDF e imágenes.   
* **Contenido multimedia**  
  Imágenes y videos asociados a productos y campañas de marketing. 

**Problemas Actuales:**

La empresa tiene los siguientes problemas actuales:  
**Integración de Datos**

* Datos aislados en distintos sistemas   
* No existe integración entre ventas físicas y online   
* Dificultad para consolidar información de clientes 

**Latencia de Información**

* Reportes con retraso de hasta 48 horas   
* No se puede monitorear ventas en tiempo real 

**Calidad de Datos**

* Duplicidad de clientes   
* Datos incompletos   
* Inconsistencias entre sistemas 

**Procesos Manuales**

* Uso intensivo de Excel para consolidación   
* Alto esfuerzo manual en reportes 

**Limitaciones Tecnológicas**

* Infraestructura local con baja escalabilidad   
* Sistemas no preparados para grandes volúmenes de datos 

 **Limitaciones Analíticas**

* No existe visión integrada del cliente   
* No se pueden realizar análisis avanzados   
* No hay base para modelos predictivos 

**Falta de Capacidades en Tiempo Real**

* No se detectan fraudes oportunamente   
* No hay recomendaciones en línea   
* No existen alertas de quiebre de stock 

**Necesidades del Negocio:**

La empresa requiere:  
**Procesamiento en tiempo real**

* Monitoreo de ventas en vivo   
* Detección de fraudes   
* Recomendaciones personalizadas   
* Alertas de inventario 

**Procesamiento batch**

* Reportes periódicos   
* Análisis histórico   
* Consolidación de información 

**Analítica avanzada**

* Segmentación de clientes   
* Predicción de demanda   
* Análisis de comportamiento 

**Restricciones:**

* No se pueden modificar los sistemas actuales   
* Se deben integrar todas las fuentes de datos   
* La solución debe ser escalable   
* Debe soportar grandes volúmenes de datos 

En base a este caso descrito, se solicita desarrollar las siguientes actividades:

1. Qué tipo de datos maneja la empresa, clasificar en:  
* Estructurados  
* Semiestructurados  
* No Estructurados

2. Identificar y describir en forma detallada problemas de la arquitectura actual  
     
3. Identificar y describir en forma detallada necesidades del negocio  
     
4. Diseñar una arquitectura que incluya:  
* Flujo de datos  
* Origen → Ingesta → Almacenamiento → Procesamiento → Consumo   
* Crear un diagrama de la arquitectura  
    
5. Realizar las siguientes definiciones y justificar las respuestas:  
* ¿ETL o ELT? ¿Por qué?   
* ¿Data warehouse, data lake o ambos?   
* ¿Uso de nube? (sí/no y por qué)   
* ¿Procesamiento batch, streaming o híbrido?   
* ¿Aplicar arquitectura Lambda?   
    
6. Describa el tipo estructura del modelo de datos del Data Warehouse, clasificación y descripción detallada de sus tablas y relaciones, cuál es su objetivo  
     
7. Describa Herramientas BI (Bussiness Intelligence) que utilizaría con el Data Warehouse, cual es su funcionalidad, justifique su respuesta  
     
8. Describa tipo de información que puede obtener mediante las herramientas BI del Data Warehouse, cual es su objetivo, incluya ejemplos  
     
9. Realice un Diagrama que muestre todos los componentes de la solución desde el origen hasta el consumo  
     
10. Describa los beneficios de la solución para el negocio  
    

![][image1]  


[image1]: <data:image/png;base64,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>