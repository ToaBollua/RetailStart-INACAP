Jueves 12 de Marzo
Arquitectura de Almacenamiento de Datos

A continuacion estare pasando en limpio el contenido del material de la Semana 1 en el ambiente de aprendizaje.

##  Introduccion

### Primero
Aprenderas que es la arquitectura de datos y como permite estructurar la informacion de forma coherente para apoyar procesos empresariales. Conoceras su importancia en distintos contextos, desde empresas publicas hasta instituciones educativas, y su rol en la toma de decisiones informadas.

### Luego
Exploraras conceptos fundamentales como data warehouse, data lake y data mart, y conoceras los procesos de integracion de datos como ETL y ELT. Tambien analizaras las bases de datos transaccionales (OLTP) y su vinculo con el analisis estrategico. Ademas descrubriras que es el almacenamiento distribuido y como las arquitecturas en la nube permiten escalar las soluciones de datos.

### Finalmente
Estaras en capacidad de diferenciar las principales soluciones de almacenamiento de datos, sus ventajas y desafios, ademas de comprender su aplicacion practica en distintos sectores. Esto te permitira interpretar y evaluar arquitecturas modernas orientadas al analisis y aprovechamiento de grandes volumenes de datos.


##  Glosario

- Arquitectura de datos moderna:
Conjunto de tecnologias, procesos y componentes que permiten gestionar datos en entornos locales, hibridos o en la nube. Facilita la toma de decisiones basada en datos de forma agil y escalable.

- Arquitectura Lambda:
Modelo que integra procesamiento en tiempo real (speed layer) y por lotes (batch layer) para una entrega de datos unificada. Es ideal para entornos donde se requiere respuesta inmediata y analisis profundo.

- Almacenamiento distribuido:
Es un modelo que reparte los datos en multiples nodos. Posee alta disponibilidad, escalabilidad horizontal y tolerancia a fallos. Es usado por plataformas que requieren continuidad operativa.

### Que es el data warehouse
Un Data Warehouse es un sistema de almacenamiento de datos diseñado especificamente para el analisis y la generacion de informes, en lugar del procesamiento de transacciones diarias.

Imagina que es una biblioteca centralizada donde se guardan versiones "limpias" y organizadas de la informacion que proviene de distintas fuentes de una empresa (ventas, inventario, marketing, etc) para que los analistas puedan tomar decisiones basadas en datos historicos.

### Que es un ERP?
Un ERP (Enterprise Resurce Planning o Plaificacion de Recursos Empresariales) es un tipo de software que las organizaciones utilizan para gestionar las actividades empresariales diarias.

Si el data warehouse que mencionamos antes era la "memoria historica" para analizar que paso, el ERP es el sistema nervioso central que controla lo que esta pasando en tiempo real. Su objetivo principal es integrar todos los departamentos de una empresa en una sola base de datos centralizada.

### Que es un SAP?
Es el gigante de los ERP. SAP (Systeme, Anwendungen und Produkte in der Datenverarbeitung) es una empresa alemana que domina el mercado del software empresarial. Si una multinacional es grande, hay un 90% de probabilidades de que use SAP para no colapsar.

Basicamente, es el software que mantiene los engranajes de una corporacion girando sin que contabilidad se pelee con porque "faltan tornillos".

No son programas sueltos. Si alguien en una fabrica en Alemania marca una pieza como "dañada", el contador en Nueva York ve reflejado en el balance de activos al segundo.

### Y que hay de Oracle Financial?

Si SAP es el gigante aleman, Oracle Financials es el peso pesado de Silicon Valley. Es la joya de la corona del ERP de Oracle y, para muchos directores financieros, es el estandar de oro en cuanto a control y cumplimiento normativo.

No es un solo programa, sino una suite de gestion financiera ultra robusta que hoy existe principalmente en dos sabores:
    Oracle E-Business Suite (EBS): La version clasica "On-Premise" (Instalada en servidores propios). Muy personalizable, pero requiere un ejercito de IT para mantenerla.

    Oracle Financials Cloud: La version moderna SaaS. Menos personalizable a nivel de codigo profundo, pero con mucha IA, actualizaciones automaticas y una interfaz que no parece de 1995.

### Que es Softland?

Seria bajar de las ligas multinacionales billonarias a la realidad local. Softland es el ERP dominante en el mercado hispanohablante, especialmente en Chile. Si SAP es un portaaviones, Softland es una camioneta 4x4: no es tan glamurosa, pero es la que mueve a las PYMES y empresas medianas de la region.

Al igual que sus hermanos mayores, funciona por modulos independientes que compar
