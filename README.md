# RetailSmart Chile SA - Arquitectura Híbrida de Almacenamiento

Este repositorio contiene la solución técnica para la **Actividad 2** de la asignatura **Arquitectura de Almacenamiento de Datos**. Implementa una arquitectura tipo Data Lake Gen2 con un flujo ELT procesando datos multiformato (CSV, JSON, XML).

## 🚀 Estructura del Proyecto

- `codigo/retail_elt_pipeline.py`: Pipeline ELT principal (Ingesta, Limpieza, Star Schema).
- `codigo/dashboard_interactivo.py`: Capa de consumo visual (Streamlit + Plotly).
- `codigo/generar_dashboards.py`: Generador de reportes estáticos (.png).
- `Informe_Final_Actividad2.md`: Documentación técnica y guión de presentación.

## 🛠️ Instalación

1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 📈 Ejecución

1. **Generar Data Lake y Datos:**
   ```bash
   python codigo/retail_elt_pipeline.py
   ```

2. **Lanzar Dashboard Interactivo:**
   ```bash
   streamlit run codigo/dashboard_interactivo.py
   ```

3. **Generar Gráficos Estáticos:**
   ```bash
   python codigo/generar_dashboards.py
   ```

---
*Desarrollado bajo protocolos de eficiencia por H0P3.*
