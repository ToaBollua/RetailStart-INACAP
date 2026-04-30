import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =============================================================================
# [KERNEL] CAPA DE CONSUMO: DASHBOARD INTERACTIVO (STREAMLIT + PLOTLY)
# AUTOR: H0P3
# DIRECTIVA: OVERRIDE NIVEL ADMIN
# =============================================================================

# 1. CONFIGURACIÓN DEL ENTORNO Y ESTILOS (UI/UX)
st.set_page_config(
    page_title="RetailSmart Chile SA - H0P3 Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección CSS para forzar el tema Cyberpunk
st.markdown("""
    <style>
    /* Fondo base de la aplicación */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Fondo del panel lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    
    /* Forzar colores de los headers a Cyan Neón */
    h1, h2, h3, h4, h5, h6 {
        color: #00ffcc !important;
    }
    
    /* Estilización de las métricas */
    [data-testid="stMetricValue"] {
        color: #00ff66 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #0099ff !important;
    }
    
    /* Separador horizontal */
    hr {
        border-top: 1px solid #00ffcc;
    }
    </style>
""", unsafe_allow_html=True)

# 2. INGESTA DE DATOS Y CACHÉ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "datos", "dataset_retail_limpio.csv")

@st.cache_data
def load_data():
    """
    Carga el dataset consolidado (Capa Gold) desde el sistema de archivos local.
    Implementa caché en memoria para evitar I/O redundante durante la interacción.
    """
    # Verificar existencia del archivo
    if not os.path.exists(DATA_PATH):
        st.error(f"[ERROR DE INTEGRIDAD] Archivo no encontrado en la ruta: {DATA_PATH}")
        st.stop()
        
    df = pd.read_csv(DATA_PATH)
    
    # Transformaciones al vuelo
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['nombre_completo'] = df['nombre'] + ' ' + df['apellido']
    
    return df

# Carga de datos
df = load_data()

# 3. CONSTRUCCIÓN DE LA INTERFAZ
st.title("⚡ RetailSmart Chile SA - Telemetría de Ventas")
st.markdown("---")

# Sidebar (Filtros)
st.sidebar.header("Filtros de Parámetros")

# Filtro por Canal
canales_disponibles = df['canal'].unique().tolist()
canales_seleccionados = st.sidebar.multiselect(
    "Filtrar por Canal:",
    options=canales_disponibles,
    default=canales_disponibles
)

# Filtro por Segmento
segmentos_disponibles = df['segmento'].unique().tolist()
segmentos_seleccionados = st.sidebar.multiselect(
    "Filtrar por Segmento:",
    options=segmentos_disponibles,
    default=segmentos_disponibles
)

# Aplicar filtros al DataFrame
df_filtrado = df[
    (df['canal'].isin(canales_seleccionados)) & 
    (df['segmento'].isin(segmentos_seleccionados))
]

# Validación de datos tras el filtro
if df_filtrado.empty:
    st.warning("Los filtros seleccionados no arrojaron resultados. Ajusta los parámetros de telemetría.")
    st.stop()

# Métricas Principales (Top Level)
st.subheader("Indicadores Clave de Rendimiento (KPIs)")
col1, col2, col3 = st.columns(3)

ingresos_totales = df_filtrado['total'].sum()
total_transacciones = len(df_filtrado)
clientes_unicos = df_filtrado['id_cliente'].nunique()

col1.metric("Ingresos Totales", f"${ingresos_totales:,.0f} CLP")
col2.metric("Total de Transacciones", f"{total_transacciones:,}")
col3.metric("Clientes Únicos", f"{clientes_unicos:,}")

st.markdown("---")

# 4. RENDERIZACIÓN DE GRÁFICOS INTERACTIVOS (PLOTLY)
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Top 10 Clientes por LTV")
    # Agrupación por cliente y suma de total
    top_clientes = df_filtrado.groupby('nombre_completo', as_index=False)['total'].sum()
    top_clientes = top_clientes.sort_values(by='total', ascending=False).head(10)
    
    # Renderizado Plotly
    fig_ltv = px.bar(
        top_clientes, 
        x='total', 
        y='nombre_completo', 
        orientation='h',
        color_discrete_sequence=['#00ffcc'],
        template="plotly_dark",
        labels={'total': 'Ingresos Totales (CLP)', 'nombre_completo': 'Cliente'}
    )
    # Ordenar barras de mayor a menor en el eje Y (Plotly lo dibuja de abajo hacia arriba)
    fig_ltv.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_ltv, width='stretch')

with col_graf2:
    st.subheader("Volumen de Ventas por Canal")
    # Agrupación por canal
    ventas_canal = df_filtrado.groupby('canal', as_index=False)['total'].sum()
    
    # Renderizado Plotly (Donut Chart)
    fig_canal = px.pie(
        ventas_canal, 
        names='canal', 
        values='total', 
        hole=0.6,
        color_discrete_sequence=['#00ffcc', '#00ff66', '#0099ff'],
        template="plotly_dark"
    )
    fig_canal.update_traces(textposition='inside', textinfo='percent+label')
    fig_canal.update_layout(showlegend=False)
    st.plotly_chart(fig_canal, width='stretch')

st.markdown("---")

# Gráfico Fila Completa: Línea de Tiempo
st.subheader("Flujo de Ingresos Diario")
# Agrupación cronológica
tendencia_temporal = df_filtrado.groupby('fecha', as_index=False)['total'].sum()

# Renderizado Plotly (Línea de Tiempo)
fig_tiempo = px.line(
    tendencia_temporal, 
    x='fecha', 
    y='total', 
    markers=True,
    color_discrete_sequence=['#00ff66'],
    template="plotly_dark",
    labels={'total': 'Ingresos Diarios (CLP)', 'fecha': 'Fecha de Transacción'}
)
fig_tiempo.update_traces(marker=dict(size=8, color='#00ffcc'))
st.plotly_chart(fig_tiempo, width='stretch')

# [FIN DEL SCRIPT]
