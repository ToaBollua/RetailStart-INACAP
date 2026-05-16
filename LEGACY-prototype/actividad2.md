Fecha: 23-04-2026

**Actividad \#2** 

**Objetivo de la actividad**

Realizar:

* Integración de datos   
* Procesamiento batch y streaming   
* Modelado de datos   
* Visualización 

**Modalidad**

* Grupos de 2 a 3 estudiantes 

**Instrucción General**  
En base al caso de la empresa **RetailStart Chile SA** descrito en la Evaluación 1, se deberá construir una solución práctica simplificada, que represente una arquitectura moderna de datos.  
Se debe realizar diseño, simulación del flujo de datos, uso de datos

**PARTE 1: Diseño Arquitectónico** 

Refinar el diseño realizado en la Evaluación 1, pero ahora con mayor detalle técnico.  
**Deben incluir:**

1. Flujo completo:   
   * Origen   
   * Ingesta   
   * Almacenamiento   
   * Procesamiento   
   * Consumo   
2. Tecnologías específicas (simuladas), por ejemplo:   
   * Ingesta: APIs / archivos CSV   
   * Almacenamiento: Data Lake (carpetas) \+ Data Warehouse   
   * Procesamiento: scripts Python   
   * Consumo: dashboard o consultas   
3. Diagramas, se puede utilizar:   
   * Draw.io   
   * PowerPoint   
     

Si deciden utilizar Data Lake”, deben indicar:

* qué tipo de datos se van a almacenar  
* cómo llegan   
* en qué formato 

**PARTE 2: Simulación de Ingesta de Datos** 

Cada grupo trabajará con **datos simulados**:  
Se encuentran disponibles los datasets (fuentes origen) en Anexo de esta actividad

**Deben:**

* Cargar los datos en Python   
* Unificar información básica 


Ejemplo de tareas:

* Leer CSV, JSON, XML   
* Limpiar datos simples (depurarlos, duplicados)   
* Unir ventas con clientes 


      Herramientas:

* Python \+ pandas 


  
**PARTE 3: Procesamiento de Datos**

Simular procesamiento tipo **ETL / ELT**  
**Deben:**

* Transformar datos:   
  * Calcular ventas totales   
  * Identificar clientes frecuentes   
* Generar dataset “limpio” para análisis 

Ejemplo:

* Total ventas por cliente   
* Total ventas por canal (tienda vs online) 


---

**PARTE 4: Modelado de Data Warehouse** 

Construir un modelo tipo **estrella**  
**Deben definir:**

* Tabla de hechos:   
  * Ventas   
* Tablas de dimensiones:   
  * Cliente   
  * Producto   
  * Tiempo   
  * Canal   
    

Pueden representarlo:

* En diagramas    
* O en tablas (Excel) 

**PARTE 5: Análisis y Visualización** 

Generar **análisis de datos**  
Opciones:

* Gráficos en Python   
* Excel   
* Power BI (si lo manejan) 


**Deben responder:**

* ¿Quiénes son los mejores clientes?   
* ¿Qué canal vende más?   
* ¿Qué producto tiene más ventas? 

**PARTE 6: Reflexión Técnica**

Responder:

* ¿Dónde aplicarían streaming?   
* ¿Cómo escalarían esta solución?   
* ¿Qué problemas reales podrían surgir? 

**Entregables** (Fecha: 14-05-2026)  
Cada grupo debe entregar:

1. Documento (PDF o Word)   
   * Arquitectura   
   * Modelo de datos   
   * Justificaciones   
       
2. Archivos de datos procesados   
   * CSV limpio   
       
3. Código Python   
   * Ingesta   
   * Transformación   
       
4. Evidencia de análisis   
   * Capturas o gráficos   
       
5. Presentación  
   * Realizar una presentación del trabajo realizado de 15 a 20 minutos

**Anexo**:

**Obligatorios:**  
ventas\_pos   
clientes\_crm   
productos\_erp   
ventas\_online   
**Opcionales :**  
eventos\_app   
logs\_sistema   
callcenter   
redes\_sociales   
logistica

Datos Fuentes Origen

**1\. ventas\_pos.csv**  
id\_venta,fecha,id\_cliente,id\_producto,cantidad,precio\_unitario,tienda  
1,2026-04-01,101,2001,2,150000,Santiago  
2,2026-04-01,102,2002,1,300000,Providencia  
3,2026-04-02,103,2003,1,50000,Maipu  
4,2026-04-02,101,2001,1,150000,Las Condes  
5,2026-04-03,104,2004,3,20000,La Florida  
6,2026-04-03,105,2002,2,300000,Puente Alto  
7,2026-04-04,106,2005,1,80000,Ñuñoa  
8,2026-04-04,107,2003,2,50000,Santiago  
9,2026-04-05,108,2006,1,120000,Providencia  
10,2026-04-05,109,2001,1,150000,Maipu

**2\. productos\_erp.csv**  
id\_producto,nombre\_producto,categoria,precio\_base,proveedor  
2001,Notebook Lenovo,Tecnologia,140000,Lenovo  
2002,Smartphone Samsung,Tecnologia,280000,Samsung  
2003,Polera Hombre,Vestuario,30000,Nike  
2004,Silla Oficina,Hogar,15000,Ikea  
2005,Audifonos Sony,Tecnologia,70000,Sony  
2006,Tablet Huawei,Tecnologia,100000,Huawei  
2007,Zapatos Mujer,Vestuario,50000,Adidas  
2008,Microondas,Hogar,80000,LG  
2009,Monitor,Tecnologia,120000,Dell  
2010,Mochila,Vestuario,25000,Puma

**3\. clientes\_crm.csv**  
id\_cliente,nombre,apellido,email,segmento,ciudad  
101,Juan,Perez,juan@email.com,Premium,Santiago  
102,Ana,Gomez,ana@email.com,Regular,Valparaiso  
103,Carlos,Rojas,carlos@email.com,Premium,Concepcion  
104,Maria,Lopez,maria@email.com,Nuevo,Santiago  
105,Pedro,Diaz,pedro@email.com,Regular,Temuco  
106,Laura,Martinez,laura@email.com,Premium,Santiago  
107,Diego,Soto,diego@email.com,Nuevo,Antofagasta  
108,Sofia,Reyes,sofia@email.com,Regular,Santiago  
109,Andres,Castro,andres@email.com,Premium,La Serena  
110,Camila,Vega,camila@email.com,Nuevo,Santiago

**4\. ventas\_online.csv**  
id\_orden,fecha,id\_cliente,total,canal  
5001,2026-04-01,101,300000,web  
5002,2026-04-02,103,50000,web  
5003,2026-04-03,104,60000,app  
5004,2026-04-03,105,300000,web  
5005,2026-04-04,106,80000,app  
5006,2026-04-04,107,100000,web  
5007,2026-04-05,108,120000,app  
5008,2026-04-05,109,150000,web  
5009,2026-04-05,110,25000,app  
5010,2026-04-05,101,150000,web

**5\. eventos\_app.json**  
\[  
{"id\_evento":1,"id\_cliente":101,"tipo":"click","producto":2001},  
{"id\_evento":2,"id\_cliente":102,"tipo":"busqueda","producto":2002},  
{"id\_evento":3,"id\_cliente":103,"tipo":"click","producto":2003},  
{"id\_evento":4,"id\_cliente":104,"tipo":"compra","producto":2004},  
{"id\_evento":5,"id\_cliente":105,"tipo":"click","producto":2002},  
{"id\_evento":6,"id\_cliente":106,"tipo":"busqueda","producto":2005},  
{"id\_evento":7,"id\_cliente":107,"tipo":"click","producto":2003},  
{"id\_evento":8,"id\_cliente":108,"tipo":"compra","producto":2006},  
{"id\_evento":9,"id\_cliente":109,"tipo":"click","producto":2001},  
{"id\_evento":10,"id\_cliente":110,"tipo":"busqueda","producto":2004}  
\]

**6\. logistica.xml**  
\<pedidos\>  
  \<pedido\>\<id\>1\</id\>\<cliente\>101\</cliente\>\<estado\>Enviado\</estado\>\</pedido\>  
  \<pedido\>\<id\>2\</id\>\<cliente\>102\</cliente\>\<estado\>Entregado\</estado\>\</pedido\>  
  \<pedido\>\<id\>3\</id\>\<cliente\>103\</cliente\>\<estado\>Pendiente\</estado\>\</pedido\>  
  \<pedido\>\<id\>4\</id\>\<cliente\>104\</cliente\>\<estado\>En tránsito\</estado\>\</pedido\>  
  \<pedido\>\<id\>5\</id\>\<cliente\>105\</cliente\>\<estado\>Entregado\</estado\>\</pedido\>  
\</pedidos\>

**7\. logs\_sistema.txt**  
2026-04-01 10:00:01 LOGIN user101  
2026-04-01 10:05:10 VIEW\_PRODUCT 2001  
2026-04-01 10:06:30 LOGOUT user101  
2026-04-02 11:00:00 LOGIN user102  
2026-04-02 11:10:22 ERROR sistema\_pago  
2026-04-02 11:15:00 LOGOUT user102

**8\. redes\_sociales.json**  
\[  
{"usuario":"cliente1","comentario":"Buen producto","rating":5},  
{"usuario":"cliente2","comentario":"Mala calidad","rating":2},  
{"usuario":"cliente3","comentario":"Excelente servicio","rating":5}  
\]

**9\. callcenter.csv**  
id\_llamada,id\_cliente,fecha,motivo,duracion  
1,101,2026-04-01,Consulta,5  
2,102,2026-04-02,Reclamo,10  
3,103,2026-04-03,Soporte,7  
4,104,2026-04-04,Consulta,4  
5,105,2026-04-05,Reclamo,12

**10\. proveedores.csv**  
id\_proveedor,nombre,producto,precio  
1,Lenovo,Notebook,140000  
2,Samsung,Smartphone,280000  
3,Nike,Polera,30000  
4,Ikea,Silla,15000  
5,Sony,Audifonos,70000

**11\. multimedia.csv**  
id\_producto,tipo,archivo  
2001,imagen,notebook.jpg  
2002,imagen,smartphone.jpg  
2003,imagen,polera.jpg  
2004,imagen,silla.jpg  
2005,video,audifonos.mp4  
