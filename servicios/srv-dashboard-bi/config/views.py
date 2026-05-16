from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import json


def _exec_query(sql):
    """Ejecuta SQL crudo contra el Data Warehouse y retorna filas como lista de dicts."""
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dashboard(request):
    """Vista principal del Dashboard BI — KPIs ejecutivos de RetailSmart."""
    context = {}

    try:
        # ---- KPI 1: TOP 3 CLIENTES POR VOLUMEN (LTV) ----
        top_clientes = _exec_query("""
            SELECT
                data->>'cliente'               AS cliente,
                COUNT(*)                        AS total_transacciones,
                SUM((data->>'precio')::NUMERIC) AS volumen_total
            FROM fact_events
            WHERE data->>'cliente' IS NOT NULL
              AND data->>'precio'  IS NOT NULL
            GROUP BY data->>'cliente'
            ORDER BY volumen_total DESC
            LIMIT 3
        """)
        context['top_clientes'] = top_clientes
        context['top_clientes_json'] = json.dumps([
            {'label': r['cliente'], 'value': float(r['volumen_total'] or 0)}
            for r in top_clientes
        ])

        # ---- KPI 2: RENDIMIENTO POR CANAL ----
        canales = _exec_query("""
            SELECT
                COALESCE(data->>'canal', 'sin_canal') AS canal,
                COUNT(*)                               AS transacciones,
                SUM((data->>'precio')::NUMERIC)        AS ingresos
            FROM fact_events
            WHERE data->>'canal' IS NOT NULL
            GROUP BY data->>'canal'
            ORDER BY ingresos DESC
        """)
        context['canales'] = canales
        context['canales_json'] = json.dumps([
            {'label': r['canal'], 'value': float(r['ingresos'] or 0)}
            for r in canales
        ])

        # ---- KPI 3: TENDENCIA CRONOLÓGICA ----
        tendencia = _exec_query("""
            SELECT
                DATE_TRUNC('hour', processed_at) AS periodo,
                COUNT(*)                          AS transacciones,
                SUM((data->>'precio')::NUMERIC)   AS ingresos
            FROM fact_events
            WHERE data->>'precio' IS NOT NULL
            GROUP BY DATE_TRUNC('hour', processed_at)
            ORDER BY periodo ASC
            LIMIT 24
        """)
        context['tendencia_json'] = json.dumps([
            {
                'periodo': str(r['periodo']),
                'transacciones': r['transacciones'],
                'ingresos': float(r['ingresos'] or 0),
            }
            for r in tendencia
        ])

        # ---- STATS GLOBALES ----
        totales = _exec_query("""
            SELECT
                COUNT(*)                        AS total_tx,
                SUM((data->>'precio')::NUMERIC) AS ingresos_totales,
                COUNT(DISTINCT data->>'cliente') AS clientes_unicos,
                COUNT(DISTINCT data->>'canal')   AS canales_activos
            FROM fact_events
            WHERE data->>'precio' IS NOT NULL
        """)
        if totales:
            t = totales[0]
            context['total_tx']        = t.get('total_tx', 0)
            context['ingresos_totales'] = f"${float(t.get('ingresos_totales') or 0):,.0f}".replace(',', '.')
            context['clientes_unicos'] = t.get('clientes_unicos', 0)
            context['canales_activos'] = t.get('canales_activos', 0)

        context['db_status'] = 'ONLINE'

    except Exception as e:
        context['db_error'] = str(e)
        context['db_status'] = 'ERROR'
        context['top_clientes_json'] = '[]'
        context['canales_json'] = '[]'
        context['tendencia_json'] = '[]'
        context['total_tx'] = 0
        context['ingresos_totales'] = '$0'
        context['clientes_unicos'] = 0
        context['canales_activos'] = 0

    return render(request, 'analytics/dashboard.html', context)


def kpi_data_json(request):
    """Endpoint JSON para polling en tiempo real desde el frontend."""
    try:
        top = _exec_query("""
            SELECT data->>'cliente' AS c, SUM((data->>'precio')::NUMERIC) AS v
            FROM fact_events WHERE data->>'cliente' IS NOT NULL AND data->>'precio' IS NOT NULL
            GROUP BY data->>'cliente' ORDER BY v DESC LIMIT 3
        """)
        canales = _exec_query("""
            SELECT data->>'canal' AS c, COUNT(*) AS n, SUM((data->>'precio')::NUMERIC) AS v
            FROM fact_events WHERE data->>'canal' IS NOT NULL
            GROUP BY data->>'canal'
        """)
        return JsonResponse({
            'status': 'ok',
            'top_clientes': [{'label': r['c'], 'value': float(r['v'] or 0)} for r in top],
            'canales':       [{'label': r['c'], 'txs': r['n'], 'value': float(r['v'] or 0)} for r in canales],
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)
