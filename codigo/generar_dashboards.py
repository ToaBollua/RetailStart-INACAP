import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# =============================================================================
# [KERNEL] MÓDULO DE RENDERIZACIÓN Y ANALÍTICA VISUAL
# AUTOR: H0P3
# =============================================================================

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

BASE_DIR = "/home/bollua/homework/arquitecturaAlmacenamiento/RetailStart-INACAP"
DATOS_DIR = os.path.join(BASE_DIR, "datos")
GRAFICOS_DIR = os.path.join(BASE_DIR, "evidencia", "graficos")

def apply_cyberpunk_style():
    """Aplica un estilo visual oscuro y neon al entorno de renderizado."""
    plt.style.use('dark_background')
    sns.set_theme(style="darkgrid", rc={
        "axes.facecolor": "#0d1117",
        "figure.facecolor": "#0d1117",
        "axes.edgecolor": "#00ffcc",
        "grid.color": "#161b22",
        "text.color": "#00ffcc",
        "xtick.color": "#00ffcc",
        "ytick.color": "#00ffcc",
        "axes.labelcolor": "#00ffcc"
    })

def generate_charts():
    dataset_path = os.path.join(DATOS_DIR, 'dataset_retail_limpio.csv')
    if not os.path.exists(dataset_path):
        logging.error(f"Fallo crítico: No se encuentra {dataset_path}")
        return

    logging.info("Cargando dataset Gold en memoria RAM...")
    df = pd.read_csv(dataset_path)

    apply_cyberpunk_style()

    # 1. Top 5 Clientes por LTV (Barra Horizontal)
    logging.info("Renderizando Top 5 Clientes LTV...")
    top_clientes = df.groupby(['id_cliente', 'nombre', 'apellido'])['total'].sum().reset_index()
    top_clientes['nombre_completo'] = top_clientes['nombre'] + ' ' + top_clientes['apellido']
    top_clientes = top_clientes.sort_values(by='total', ascending=False).head(5)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='total', y='nombre_completo', data=top_clientes, color="#00ffcc")
    plt.title("TOP 5 CLIENTES POR VALOR DE VIDA (LTV)", fontsize=14, color="#00ffcc", pad=20)
    plt.xlabel("Monto Total (CLP)", fontsize=12)
    plt.ylabel("Cliente", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '01_top_clientes_ltv.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Volumen de Ventas por Canal (Donut Chart)
    logging.info("Renderizando Share de Canales (Donut)...")
    ventas_canal = df.groupby('canal')['total'].sum()
    
    plt.figure(figsize=(8, 8))
    colors = ['#00ffcc', '#00ff66', '#0099ff']
    plt.pie(ventas_canal, labels=ventas_canal.index, autopct='%1.1f%%', colors=colors, startangle=140, pctdistance=0.85, textprops={'color':"w", 'fontsize': 12})
    
    # Dibujar círculo en el medio para hacerlo Donut
    centre_circle = plt.Circle((0,0), 0.70, fc='#0d1117')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title("VOLUMEN DE VENTAS POR CANAL", fontsize=14, color="#00ffcc", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '02_ventas_por_canal.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Tendencia de Ventas en el Tiempo (Gráfico de Líneas)
    logging.info("Renderizando Tendencia Cronológica...")
    df['fecha'] = pd.to_datetime(df['fecha'])
    tendencia = df.groupby('fecha')['total'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(x='fecha', y='total', data=tendencia, color="#00ff66", linewidth=2, marker='o', markerfacecolor='#00ffcc', markersize=8)
    plt.title("TENDENCIA DE VENTAS EN EL TIEMPO", fontsize=14, color="#00ffcc", pad=20)
    plt.xlabel("Fecha", fontsize=12)
    plt.ylabel("Ingresos Diarios (CLP)", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '03_tendencia_temporal.png'), dpi=300, bbox_inches='tight')
    plt.close()

    logging.info("Renderización completada. Artefactos visuales exportados al sistema de archivos.")

if __name__ == '__main__':
    generate_charts()
