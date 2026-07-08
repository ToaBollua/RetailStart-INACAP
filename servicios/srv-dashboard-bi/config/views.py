import csv
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import connection

# reportlab imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def _exec_query_params(sql, params=None):
    """Ejecuta SQL con parámetros y retorna filas como dicts."""
    with connection.cursor() as cursor:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        if cursor.description is None:
            return []
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dashboard(request):
    """Vista principal del Dashboard BI — KPIs ejecutivos de RetailSmart (Estrella DW con filtros)."""
    context = {}

    # 1. Leer parámetros del filtro
    start_date = request.GET.get('start_date', '2026-04-01')
    end_date = request.GET.get('end_date', '2026-04-10')
    canal_filter = request.GET.get('canal', '')
    tienda_filter = request.GET.get('tienda', '')
    segmento_filter = request.GET.get('segmento', '')

    context['start_date'] = start_date
    context['end_date'] = end_date
    context['canal_filter'] = canal_filter
    context['tienda_filter'] = tienda_filter
    context['segmento_filter'] = segmento_filter

    try:
        # Obtener opciones para los selects de filtros
        opt_canales = _exec_query_params("SELECT canal FROM dim_canal ORDER BY canal;")
        context['opt_canales'] = [r['canal'] for r in opt_canales]
        
        opt_tiendas = _exec_query_params("SELECT nombre_tienda FROM dim_tienda WHERE nombre_tienda != 'Desconocido' ORDER BY nombre_tienda;")
        context['opt_tiendas'] = [r['nombre_tienda'] for r in opt_tiendas]
        
        opt_segmentos = _exec_query_params("SELECT DISTINCT segmento FROM dim_cliente WHERE segmento != 'N/A' ORDER BY segmento;")
        context['opt_segmentos'] = [r['segmento'] for r in opt_segmentos]

        # Total ventas sin filtrar para el indicador
        total_db_ventas = _exec_query_params("SELECT COUNT(*) AS total FROM fact_ventas;")
        context['total_ventas_db'] = total_db_ventas[0]['total'] if total_db_ventas else 0

        # Construir condición WHERE dinámica
        where_clauses = ["f.fecha >= %s", "f.fecha <= %s"]
        params = [start_date, end_date]

        if canal_filter:
            where_clauses.append("f.canal = %s")
            params.append(canal_filter)
        if tienda_filter:
            where_clauses.append("st.nombre_tienda = %s")
            params.append(tienda_filter)
        if segmento_filter:
            where_clauses.append("c.segmento = %s")
            params.append(segmento_filter)

        where_sql = " AND ".join(where_clauses)

        # ---- KPI 1: TOP 10 CLIENTES POR LTV ----
        top_clientes = _exec_query_params(f"""
            SELECT
                c.nombre || ' ' || c.apellido AS cliente,
                COUNT(f.id_transaccion)        AS total_transacciones,
                SUM(f.total)                   AS volumen_total
            FROM fact_ventas f
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY c.id_cliente, c.nombre, c.apellido
            ORDER BY volumen_total DESC
            LIMIT 10;
        """, params)
        context['top_clientes'] = top_clientes[:3]
        context['top_clientes_json'] = json.dumps([
            {'label': r['cliente'], 'value': float(r['volumen_total'] or 0)}
            for r in top_clientes
        ])

        # ---- KPI 2: CANALES ----
        canales = _exec_query_params(f"""
            SELECT
                ch.canal                        AS canal,
                COUNT(f.id_transaccion)        AS transacciones,
                SUM(f.total)                   AS ingresos
            FROM fact_ventas f
            JOIN dim_canal ch ON f.canal = ch.canal
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY ch.canal
            ORDER BY ingresos DESC;
        """, params)
        context['canales'] = canales
        context['canales_json'] = json.dumps([
            {'label': r['canal'], 'value': float(r['ingresos'] or 0)}
            for r in canales
        ])

        # ---- KPI 3: TENDENCIA DIARIA ----
        tendencia = _exec_query_params(f"""
            SELECT
                t.fecha                        AS periodo,
                COUNT(f.id_transaccion)        AS transacciones,
                SUM(f.total)                   AS ingresos
            FROM fact_ventas f
            JOIN dim_tiempo t ON f.fecha = t.fecha
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY t.fecha
            ORDER BY t.fecha ASC;
        """, params)
        context['tendencia_json'] = json.dumps([
            {
                'periodo': str(r['periodo']),
                'transacciones': r['transacciones'],
                'ingresos': float(r['ingresos'] or 0),
            }
            for r in tendencia
        ])

        # ---- KPI 4: TOP PRODUCTOS ----
        top_productos = _exec_query_params(f"""
            SELECT
                p.nombre_producto              AS producto,
                SUM(f.cantidad)                AS cantidad_vendida,
                SUM(f.total)                   AS volumen_total
            FROM fact_ventas f
            JOIN dim_producto p ON f.id_producto = p.id_producto
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY p.id_producto, p.nombre_producto
            ORDER BY volumen_total DESC
            LIMIT 10;
        """, params)
        context['top_productos_json'] = json.dumps([
            {'label': r['producto'], 'value': float(r['volumen_total'] or 0), 'qty': int(r['cantidad_vendida'] or 0)}
            for r in top_productos
        ])

        # ---- KPI 5: VENTAS POR CATEGORÍA ----
        categoria_ventas = _exec_query_params(f"""
            SELECT
                p.categoria                    AS categoria,
                SUM(f.total)                   AS ingresos
            FROM fact_ventas f
            JOIN dim_producto p ON f.id_producto = p.id_producto
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY p.categoria
            ORDER BY ingresos DESC;
        """, params)
        context['categorias_json'] = json.dumps([
            {'label': r['categoria'], 'value': float(r['ingresos'] or 0)}
            for r in categoria_ventas
        ])

        # ---- KPI 6: VENTAS POR TIENDA ----
        tiendas_ventas = _exec_query_params(f"""
            SELECT
                st.nombre_tienda               AS tienda,
                st.region                      AS region,
                SUM(f.total)                   AS ingresos
            FROM fact_ventas f
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            WHERE {where_sql}
            GROUP BY st.tienda_key, st.nombre_tienda, st.region
            ORDER BY ingresos DESC;
        """, params)
        context['tiendas_json'] = json.dumps([
            {'label': f"{r['tienda']} ({r['region']})", 'value': float(r['ingresos'] or 0)}
            for r in tiendas_ventas if r['tienda'] != 'Desconocido'
        ])

        # ---- KPI 7: VENTAS POR SEGMENTO ----
        segmento_ventas = _exec_query_params(f"""
            SELECT
                c.segmento                     AS segmento,
                SUM(f.total)                   AS ingresos
            FROM fact_ventas f
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql}
            GROUP BY c.segmento
            ORDER BY ingresos DESC;
        """, params)
        context['segmentos_json'] = json.dumps([
            {'label': r['segmento'], 'value': float(r['ingresos'] or 0)}
            for r in segmento_ventas if r['segmento'] != 'N/A'
        ])

        # ---- STATS GLOBALES ----
        totales = _exec_query_params(f"""
            SELECT
                COUNT(f.id_transaccion)        AS total_tx,
                SUM(f.total)                   AS ingresos_totales,
                COUNT(DISTINCT f.id_cliente)   AS clientes_unicos,
                COUNT(DISTINCT f.canal)        AS canales_activos,
                AVG(f.total)                   AS promedio_tx
            FROM fact_ventas f
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            JOIN dim_tienda st ON f.tienda_key = st.tienda_key
            WHERE {where_sql};
        """, params)
        if totales:
            t = totales[0]
            context['total_tx']        = t.get('total_tx', 0)
            context['count_results']   = t.get('total_tx', 0)
            context['ingresos_totales'] = f"${float(t.get('ingresos_totales') or 0):,.0f}".replace(',', '.')
            context['clientes_unicos'] = t.get('clientes_unicos', 0)
            context['canales_activos'] = t.get('canales_activos', 0)
            context['promedio_tx']     = f"${float(t.get('promedio_tx') or 0):,.0f}".replace(',', '.')

        context['db_status'] = 'ONLINE'

    except Exception as e:
        context['db_error'] = str(e)
        context['db_status'] = 'ERROR'
        context['top_clientes_json'] = '[]'
        context['canales_json'] = '[]'
        context['tendencia_json'] = '[]'
        context['top_productos_json'] = '[]'
        context['categorias_json'] = '[]'
        context['tiendas_json'] = '[]'
        context['segmentos_json'] = '[]'
        context['total_tx'] = 0
        context['count_results'] = 0
        context['total_ventas_db'] = 0
        context['ingresos_totales'] = '$0'
        context['clientes_unicos'] = 0
        context['canales_activos'] = 0
        context['promedio_tx'] = '$0'

    return render(request, 'analytics/dashboard.html', context)

def kpi_data_json(request):
    """Endpoint JSON para polling en tiempo real desde el frontend."""
    try:
        top = _exec_query_params("""
            SELECT c.nombre || ' ' || c.apellido AS c, SUM(f.total) AS v
            FROM fact_ventas f
            JOIN dim_cliente c ON f.id_cliente = c.id_cliente
            GROUP BY c.id_cliente, c.nombre, c.apellido ORDER BY v DESC LIMIT 3
        """)
        canales = _exec_query_params("""
            SELECT canal AS c, COUNT(*) AS n, SUM(total) AS v
            FROM fact_ventas GROUP BY canal
        """)
        return JsonResponse({
            'status': 'ok',
            'top_clientes': [{'label': r['c'], 'value': float(r['v'] or 0)} for r in top],
            'canales':       [{'label': r['c'], 'txs': r['n'], 'value': float(r['v'] or 0)} for r in canales],
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)

def export_csv(request):
    """Exporta el contenido de fact_ventas a un archivo CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fact_ventas_dw.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['id_transaccion', 'fecha', 'cliente', 'producto', 'categoria', 'canal', 'tienda', 'cantidad', 'precio_unitario', 'total', 'tipo_venta'])
    
    rows = _exec_query_params("""
        SELECT 
            f.id_transaccion,
            f.fecha,
            c.nombre || ' ' || c.apellido AS cliente,
            p.nombre_producto AS producto,
            p.categoria,
            f.canal,
            t.nombre_tienda AS tienda,
            f.cantidad,
            f.precio_unitario,
            f.total,
            f.tipo_venta
        FROM fact_ventas f
        LEFT JOIN dim_cliente c ON f.id_cliente = c.id_cliente
        LEFT JOIN dim_producto p ON f.id_producto = p.id_producto
        LEFT JOIN dim_tienda t ON f.tienda_key = t.tienda_key
        ORDER BY f.fecha DESC;
    """)
    
    for r in rows:
        writer.writerow([
            r['id_transaccion'], r['fecha'], r['cliente'], r['producto'], 
            r['categoria'], r['canal'], r['tienda'], r['cantidad'], 
            r['precio_unitario'], r['total'], r['tipo_venta']
        ])
    return response

def export_json(request):
    """Exporta el contenido de fact_ventas a un archivo JSON."""
    rows = _exec_query_params("""
        SELECT 
            f.id_transaccion,
            f.fecha,
            c.nombre || ' ' || c.apellido AS cliente,
            p.nombre_producto AS producto,
            p.categoria,
            f.canal,
            t.nombre_tienda AS tienda,
            f.cantidad,
            f.precio_unitario,
            f.total,
            f.tipo_venta
        FROM fact_ventas f
        LEFT JOIN dim_cliente c ON f.id_cliente = c.id_cliente
        LEFT JOIN dim_producto p ON f.id_producto = p.id_producto
        LEFT JOIN dim_tienda t ON f.tienda_key = t.tienda_key
        ORDER BY f.fecha DESC;
    """)
    response = HttpResponse(json.dumps(rows, default=str, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="fact_ventas_dw.json"'
    return response

def export_pdf(request):
    """Genera un reporte en PDF (consolidado o filtrado) utilizando ReportLab."""
    start_date = request.GET.get('start_date', '2026-04-01')
    end_date = request.GET.get('end_date', '2026-04-10')
    canal_filter = request.GET.get('canal', '')
    tienda_filter = request.GET.get('tienda', '')
    segmento_filter = request.GET.get('segmento', '')

    is_filtered = canal_filter or tienda_filter or segmento_filter or (start_date != '2026-04-01') or (end_date != '2026-04-10')

    # Construir condición WHERE
    where_clauses = ["f.fecha >= %s", "f.fecha <= %s"]
    params = [start_date, end_date]

    if canal_filter:
        where_clauses.append("f.canal = %s")
        params.append(canal_filter)
    if tienda_filter:
        where_clauses.append("st.nombre_tienda = %s")
        params.append(tienda_filter)
    if segmento_filter:
        where_clauses.append("c.segmento = %s")
        params.append(segmento_filter)

    where_sql = " AND ".join(where_clauses)

    sql = f"""
        SELECT 
            f.id_transaccion,
            f.fecha,
            c.nombre || ' ' || c.apellido AS cliente,
            p.nombre_producto AS producto,
            f.canal,
            st.nombre_tienda AS tienda,
            f.cantidad,
            f.total
        FROM fact_ventas f
        LEFT JOIN dim_cliente c ON f.id_cliente = c.id_cliente
        LEFT JOIN dim_producto p ON f.id_producto = p.id_producto
        LEFT JOIN dim_tienda st ON f.tienda_key = st.tienda_key
        WHERE {where_sql}
        ORDER BY f.fecha ASC;
    """
    rows = _exec_query_params(sql, params)

    total_sales = sum(float(r['total'] or 0) for r in rows)
    total_qty = sum(int(r['cantidad'] or 0) for r in rows)
    avg_ticket = total_sales / len(rows) if rows else 0

    response = HttpResponse(content_type='application/pdf')
    filename = "reporte_filtrado.pdf" if is_filtered else "reporte_consolidado.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0d3b0d'),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=20
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#0d3b0d'),
        spaceBefore=15,
        spaceAfter=10
    )

    story.append(Paragraph("RETAILSMART CHILE SA — INFORME DE NEGOCIOS", title_style))
    report_type = "PERSONALIZADO / FILTRADO" if is_filtered else "CONSOLIDADO GENERAL"
    story.append(Paragraph(f"Tipo de Reporte: {report_type} · Periodo: {start_date} al {end_date}", subtitle_style))
    story.append(Spacer(1, 10))

    if is_filtered:
        filter_text = "<b>Filtros Aplicados:</b>"
        if canal_filter: filter_text += f" Canal: {canal_filter} |"
        if tienda_filter: filter_text += f" Tienda: {tienda_filter} |"
        if segmento_filter: filter_text += f" Segmento: {segmento_filter} |"
        story.append(Paragraph(filter_text.strip(" |"), styles['Normal']))
        story.append(Spacer(1, 10))

    summary_data = [
        ["Total Transacciones", "Total Ingresos (CLP)", "Ticket Promedio (CLP)", "Unidades Vendidas"],
        [str(len(rows)), f"${total_sales:,.0f}".replace(",", "."), f"${avg_ticket:,.0f}".replace(",", "."), f"{total_qty} uds"]
    ]
    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d3b0d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f2f7f2')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#d0ebd0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Detalle de Ventas Consolidadas", section_style))
    table_data = [["Fecha", "Cliente", "Producto", "Canal", "Tienda", "Cantidad", "Total"]]
    truncated = len(rows) > 35
    display_rows = rows[:35]

    for r in display_rows:
        table_data.append([
            str(r['fecha']),
            r['cliente'][:18] if r['cliente'] else '',
            r['producto'][:20] if r['producto'] else '',
            str(r['canal']),
            str(r['tienda']),
            str(r['cantidad']),
            f"${float(r['total'] or 0):,.0f}".replace(",", ".")
        ])

    detail_table = Table(table_data, colWidths=[65, 95, 110, 60, 80, 50, 70])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#336633')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0ebd0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fcf9')]),
    ]))
    story.append(detail_table)

    if truncated:
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<i>* Mostrando las primeras 35 transacciones de un total de {len(rows)} resultados. Para descargar la sábana completa, exporte en CSV o JSON.</i>", styles['Normal']))

    doc.build(story)
    return response

