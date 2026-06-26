#!/usr/bin/env python3
"""
RetailSmart — CSV CLI Dashboard Interactivo
Carga un CSV de transacciones POS u Online y los transmite en vivo al endpoint
/ingest de srv-api-backend, mostrando un dashboard en terminal con métricas
en tiempo real.

Uso:
    python test_csv_cli.py                          # modo interactivo (elige un CSV)
    python test_csv_cli.py --file datasets/ventas_pos/dia1/transaccion_pos_101.csv
    python test_csv_cli.py --dir  datasets/ventas_pos/dia1/
    python test_csv_cli.py --day  dia1              # carga todos los días
    python test_csv_cli.py --all                    # carga los 5 días completos
"""

import argparse
import csv
import glob
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────
API_URL   = "http://localhost:8000/ingest"
HEALTH_URL= "http://localhost:8000/buffer"
BASE_DIR  = Path(__file__).parent
DELAY_MS  = 60   # delay entre requests en ms (ajustar para demostraciones)

# ─── COLORES ANSI (verde neón) ────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    NEON   = "\033[38;5;82m"      # verde brillante
    GREEN  = "\033[38;5;46m"      # verde estándar
    DIM    = "\033[38;5;240m"
    YELLOW = "\033[38;5;190m"
    RED    = "\033[38;5;196m"
    CYAN   = "\033[38;5;51m"
    BOLD   = "\033[1m"
    BG_BLK = "\033[40m"

def neon(s):   return f"{C.NEON}{s}{C.RESET}"
def dim(s):    return f"{C.DIM}{s}{C.RESET}"
def green(s):  return f"{C.GREEN}{s}{C.RESET}"
def red(s):    return f"{C.RED}{s}{C.RESET}"
def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"
def bold(s):   return f"{C.BOLD}{s}{C.RESET}"

# ─── UTILIDADES DE TERMINAL ───────────────────────────────────────────────────
TERM_WIDTH = os.get_terminal_size().columns if sys.stdout.isatty() else 100

def divider(char="─", color=C.DIM):
    print(f"{color}{char * TERM_WIDTH}{C.RESET}")

def header():
    os.system("clear || cls")
    print()
    divider("═", C.NEON)
    print(f"{C.NEON}{C.BOLD}{'RETAILSMART // CSV INGESTION CLI DASHBOARD v1.0':^{TERM_WIDTH}}{C.RESET}")
    print(f"{C.DIM}{'GLITCHPOINT PROTOCOL // H0P3 NODE ACTIVE':^{TERM_WIDTH}}{C.RESET}")
    divider("═", C.NEON)
    print()

def ts():
    return dim(f"[{datetime.now().strftime('%H:%M:%S')}]")

def log(msg, level="INFO"):
    icons = {"INFO": dim("·"), "OK": neon("✓"), "ERR": red("✗"), "WARN": yellow("⚠"), "TX": green("→"), "DONE": neon("★")}
    labels = {"INFO": dim("INFO"), "OK": neon("OK  "), "ERR": red("ERR "), "WARN": yellow("WARN"), "TX": green("TX  "), "DONE": neon("DONE")}
    print(f"  {ts()} {labels.get(level, dim(level))}  {msg}")

def progress_bar(current, total, width=40):
    if total == 0:
        return "[" + " " * width + "]  0%"
    pct = current / total
    filled = int(width * pct)
    bar = neon("█" * filled) + dim("░" * (width - filled))
    pct_str = f"{pct * 100:5.1f}%"
    return f"[{bar}] {neon(pct_str)}"

def print_stats_panel(stats, elapsed=0):
    print()
    divider()
    ok_rate = (stats['ok'] / stats['total'] * 100) if stats['total'] > 0 else 0
    tx_s    = stats['total'] / max(elapsed, 0.001)
    cols = [
        ("TX ENVIADAS",  neon(str(stats['total'])),  ""),
        ("EXITOSAS",     neon(str(stats['ok'])),      ""),
        ("ERRORES",      red(str(stats['err'])),      ""),
        ("TASA OK",      neon(f"{ok_rate:.1f}%"),     ""),
        ("TX/seg",       cyan(f"{tx_s:.1f}"),         ""),
        ("TIEMPO",       yellow(f"{elapsed:.1f}s"),   ""),
    ]
    col_w = TERM_WIDTH // len(cols)
    header_row = ""
    value_row  = ""
    for label, value, _ in cols:
        header_row += f"  {dim(label):<{col_w}}"
        value_row  += f"  {C.BOLD}{value:<{col_w}}{C.RESET}"
    print(header_row)
    print(value_row)
    divider()
    print()

# ─── API ──────────────────────────────────────────────────────────────────────
def check_api():
    try:
        req = urllib.request.urlopen(HEALTH_URL, timeout=3)
        data = json.loads(req.read())
        return True, data.get("buffer_size", "?")
    except Exception as e:
        return False, str(e)

def send_tx(payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=5)
    return json.loads(resp.read())

# ─── CSV DETECTION & PARSING ──────────────────────────────────────────────────
def detect_type(headers: list):
    if "id_venta" in headers:
        return "POS"
    if "id_orden" in headers:
        return "ONLINE"
    return None

def infer_date(filepath: Path) -> str:
    path_str = str(filepath).lower()
    if "dia1" in path_str or "dia_1" in path_str:
        return "2026-04-01"
    elif "dia2" in path_str or "dia_2" in path_str:
        return "2026-04-02"
    elif "dia3" in path_str or "dia_3" in path_str:
        return "2026-04-03"
    elif "dia4" in path_str or "dia_4" in path_str:
        return "2026-04-04"
    elif "dia5" in path_str or "dia_5" in path_str:
        return "2026-04-05"
    return None

def parse_row_pos(row: dict, date_override=None):
    id_venta = row.get("id_venta", "?")
    fecha    = date_override if date_override else row.get("fecha", "2026-01-01")
    id_cli   = row.get("id_cliente", "?")
    id_prod  = row.get("id_producto", "?")
    cantidad = float(row.get("cantidad", 1))
    precio_u = float(row.get("precio_unitario", 0))
    tienda   = row.get("tienda", "?")
    return {
        "id": f"POS-{id_venta}",
        "data": {
            "sku":       id_prod,
            "canal":     "tienda_fisica",
            "cliente":   id_cli,
            "precio":    cantidad * precio_u,
            "timestamp": f"{fecha}T12:00:00.000Z",
            "nodo":      "csv-cli-dashboard",
            "_tienda":   tienda,
        }
    }

def parse_row_online(row: dict, date_override=None):
    id_orden = row.get("id_orden", "?")
    fecha    = date_override if date_override else row.get("fecha", "2026-01-01")
    id_cli   = row.get("id_cliente", "?")
    total    = float(row.get("total", 0))
    canal    = row.get("canal", "web")
    return {
        "id": f"WEB-{id_orden}",
        "data": {
            "sku":       "N/A",
            "canal":     canal,
            "cliente":   id_cli,
            "precio":    total,
            "timestamp": f"{fecha}T12:00:00.000Z",
            "nodo":      "csv-cli-dashboard",
        }
    }

# ─── INGEST FILE ──────────────────────────────────────────────────────────────
def ingest_file(filepath: Path, stats: dict, verbose=True):
    if not filepath.exists():
        log(f"Archivo no encontrado: {filepath}", "ERR")
        return

    date_override = infer_date(filepath)

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers_lower = [h.strip().lower() for h in (reader.fieldnames or [])]
        csv_type = detect_type(headers_lower)

        if not csv_type:
            log(f"Esquema desconocido en {filepath.name}. Saltando.", "WARN")
            return

        rows = list(reader)

    if verbose:
        log(f"Abriendo {neon(filepath.name)} | tipo={cyan(csv_type)} | filas={len(rows)} | override_fecha={yellow(str(date_override))}", "INFO")

    for i, raw_row in enumerate(rows):
        # Normalizar keys a lowercase
        row = {k.strip().lower(): v.strip() for k, v in raw_row.items()}
        payload = parse_row_pos(row, date_override) if csv_type == "POS" else parse_row_online(row, date_override)
        tx_id   = payload["id"]
        precio  = payload["data"]["precio"]

        stats["total"] += 1

        try:
            resp = send_tx(payload)
            stats["ok"] += 1
            if verbose:
                log(
                    f"{neon(tx_id)} | cliente={cyan(payload['data']['cliente'])} | "
                    f"precio=${neon(f'{precio:,.0f}')} | canal={yellow(payload['data']['canal'])} | buf={resp.get('buffer_size','?')}",
                    "TX"
                )
        except Exception as e:
            stats["err"] += 1
            if verbose:
                log(f"{tx_id} → {red(str(e))}", "ERR")

        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000)

# ─── INTERACTIVE FILE PICKER ──────────────────────────────────────────────────
def interactive_picker():
    csv_files = sorted(BASE_DIR.rglob("*.csv"))
    if not csv_files:
        log("No se encontraron archivos CSV en el directorio del proyecto.", "ERR")
        sys.exit(1)

    print(neon(f"\n  Archivos CSV disponibles ({len(csv_files)} encontrados):\n"))
    for i, f in enumerate(csv_files):
        rel = f.relative_to(BASE_DIR)
        print(f"  {dim(f'[{i:02d}]')}  {neon(str(rel))}")

    print()
    try:
        choice = input(f"  {dim('>')} {neon('Ingresa el número o ruta del archivo: ')}")
    except (KeyboardInterrupt, EOFError):
        print("\n  Abortado por el usuario.")
        sys.exit(0)

    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(csv_files):
            return [csv_files[idx]]
        else:
            log("Índice fuera de rango.", "ERR")
            sys.exit(1)
    else:
        p = Path(choice)
        if p.exists():
            return [p]
        log(f"Archivo no encontrado: {choice}", "ERR")
        sys.exit(1)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    global DELAY_MS  # declarar primero antes de cualquier referencia

    _default_delay = DELAY_MS
    parser = argparse.ArgumentParser(description="RetailSmart CSV CLI Dashboard")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", metavar="PATH", help="Cargar un archivo CSV específico")
    group.add_argument("--dir",  metavar="DIR",  help="Cargar todos los CSV de un directorio")
    group.add_argument("--day",  metavar="DIA",  help="Cargar todos los CSV del día (ej: dia1)")
    group.add_argument("--all",  action="store_true", help="Cargar los 5 días completos")
    parser.add_argument("--delay", type=int, default=_default_delay, help=f"Delay entre requests en ms (default: {_default_delay})")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso (solo resumen final)")
    args = parser.parse_args()

    DELAY_MS = args.delay

    header()

    # ── API health ──
    api_ok, buf = check_api()
    if api_ok:
        log(f"API backend {neon('ONLINE')} en {cyan(API_URL)} | buffer: {buf}", "OK")
    else:
        log(f"API backend {red('OFFLINE')} — Asegúrate que srv-api-backend esté corriendo en :8000", "ERR")
        log(f"  Detalle: {dim(str(buf))}", "WARN")
        sys.exit(1)
    print()

    # ── Resolve files ──
    files = []
    if args.file:
        files = [Path(args.file)]
    elif args.dir:
        d = Path(args.dir)
        files = sorted(d.glob("*.csv"))
        if not files:
            log(f"No se encontraron CSV en {args.dir}", "ERR")
            sys.exit(1)
    elif args.day:
        # POS individuale por día + online por día
        pos_dir = BASE_DIR / "datasets" / "ventas_pos" / args.day
        online_file = BASE_DIR / "datasets" / "ventas_online" / f"{args.day}.csv"
        files = sorted(pos_dir.glob("*.csv")) if pos_dir.exists() else []
        if online_file.exists():
            files.append(online_file)
        if not files:
            log(f"No se encontraron archivos para {args.day}", "ERR")
            sys.exit(1)
    elif args.all:
        for day in ["dia1", "dia2", "dia3", "dia4", "dia5"]:
            pos_dir = BASE_DIR / "datasets" / "ventas_pos" / day
            online_file = BASE_DIR / "datasets" / "ventas_online" / f"{day}.csv"
            if pos_dir.exists():
                files.extend(sorted(pos_dir.glob("*.csv")))
            if online_file.exists():
                files.append(online_file)
    else:
        # modo interactivo
        files = interactive_picker()
        print()

    if not files:
        log("No hay archivos para procesar.", "ERR")
        sys.exit(1)

    log(f"Archivos a procesar: {neon(str(len(files)))}", "INFO")
    print()

    # ── RUN ──
    stats = {"total": 0, "ok": 0, "err": 0}
    t0 = time.time()
    verbose = not args.quiet

    for filepath in files:
        if verbose:
            divider("·")
        ingest_file(Path(filepath), stats, verbose=verbose)

    elapsed = time.time() - t0

    # ── FINAL SUMMARY ──
    print()
    divider("═", C.NEON)
    print(f"{C.NEON}{C.BOLD}{'INGESTA COMPLETADA':^{TERM_WIDTH}}{C.RESET}")
    divider("═", C.NEON)
    print_stats_panel(stats, elapsed)

    if stats['err'] == 0:
        log(f"Pipeline limpio. {neon('0 errores')} en {len(files)} archivos.", "DONE")
    else:
        log(f"Pipeline con {red(str(stats['err']))} errores de {stats['total']} transacciones.", "WARN")
    print()

if __name__ == "__main__":
    main()
