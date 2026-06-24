const API_URL = 'http://localhost:8000/ingest';

let stats = { total: 0, ok: 0, err: 0 };
let selectedCanal = 'web';

// --- RELOJ ---
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    `[${now.toLocaleDateString('es-CL')} ${now.toTimeString().slice(0, 8)}]`;
}
setInterval(updateClock, 1000);
updateClock();

// --- CANAL BUTTONS ---
document.querySelectorAll('.canal-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    selectedCanal = btn.dataset.canal;
    document.getElementById('canal').value = selectedCanal;
    document.querySelectorAll('.canal-btn').forEach(b => {
      b.style.background = 'transparent';
      b.style.boxShadow = '';
      b.style.textShadow = '';
    });
    btn.style.background = 'rgba(0,255,204,0.12)';
    btn.style.boxShadow = '0 0 12px rgba(0,255,204,0.5)';
    btn.style.textShadow = '0 0 8px #00FFCC';
  });
});
// Activar 'web' por defecto
document.querySelector('[data-canal="web"]').click();

// --- LOGGER ---
function log(msg, type = 'info') {
  const terminal = document.getElementById('log-terminal');
  const entry = document.createElement('div');
  entry.classList.add('log-entry');

  const ts = new Date().toTimeString().slice(0, 8);
  const colors = {
    info:    'color: #888;',
    success: 'color: #00FFCC; text-shadow: 0 0 6px rgba(0,255,204,0.5);',
    error:   'color: #FF4444;',
    tx:      'color: #00FF66;',
    warn:    'color: #FFAA00;',
  };

  entry.style.cssText = colors[type] || colors.info;
  entry.textContent = `[${ts}] ${msg}`;
  terminal.appendChild(entry);
  terminal.scrollTop = terminal.scrollHeight;
}

function updateStats() {
  document.getElementById('stat-total').textContent = stats.total;
  document.getElementById('stat-ok').textContent = stats.ok;
  document.getElementById('stat-err').textContent = stats.err;
}

// --- CLEAR ---
document.getElementById('btn-clear').addEventListener('click', () => {
  document.getElementById('log-terminal').innerHTML = '';
  log('Terminal limpiada por el operador.', 'warn');
});

// --- TRANSACCIÓN ---
document.getElementById('btn-transact').addEventListener('click', async () => {
  const sku    = document.getElementById('sku').value;
  const canal  = selectedCanal;
  const cliente = document.getElementById('cliente').value;
  const precio = parseFloat(document.getElementById('precio').value);
  const txId   = `TX-${Date.now().toString(16).toUpperCase()}`;

  stats.total++;
  updateStats();

  const payload = {
    id: txId,
    data: {
      sku,
      canal,
      cliente,
      precio,
      timestamp: new Date().toISOString(),
      nodo: 'dashboard-cliente-v1',
    }
  };

  log(`Armando payload → id: ${txId}`, 'info');
  log(`SKU: ${sku} | Canal: ${canal} | Cliente: ${cliente} | Precio: $${precio.toLocaleString('es-CL')}`, 'info');
  log(`Enviando al Data Lake via POST /ingest...`, 'warn');

  const btn = document.getElementById('btn-transact');
  btn.disabled = true;
  btn.textContent = '⏳ PROCESANDO...';

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const json = await res.json();
    stats.ok++;
    log(`[SUCCESS] Transacción ${txId} enviada al Data Lake.`, 'success');
    log(`Buffer actual del API: ${json.buffer_size} registros en cola.`, 'tx');
  } catch (err) {
    stats.err++;
    log(`[ERROR] Fallo en transmisión: ${err.message}`, 'error');
    log(`Verifica que srv-api-backend esté corriendo en :8000`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ EJECUTAR TRANSACCIÓN';
    updateStats();
  }
});

// --- CARGA DE ARCHIVO CSV Y PARSING ---
const fileInput = document.getElementById('csv-file');
const selectBtn = document.getElementById('btn-select-file');
const uploadBtn = document.getElementById('btn-upload-csv');
const statusDiv = document.getElementById('file-status');

selectBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    statusDiv.textContent = `Archivo: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    statusDiv.style.color = '#00FFCC';
    uploadBtn.disabled = false;
    log(`[INFO] Archivo cargado listo para procesamiento: ${file.name}`, 'warn');
  } else {
    statusDiv.textContent = 'Ningún archivo cargado.';
    statusDiv.style.color = '';
    uploadBtn.disabled = true;
  }
});

uploadBtn.addEventListener('click', () => {
  const file = fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const text = e.target.result;
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
    
    if (lines.length <= 1) {
      log('[ERROR] El archivo está vacío o no contiene datos válidos.', 'error');
      return;
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    log(`[CSV] Detectadas cabeceras: [${headers.join(', ')}]`, 'info');

    // Identificar el tipo de dataset (POS o WEB)
    const isPOS = headers.includes('id_venta');
    const isOnline = headers.includes('id_orden');

    if (!isPOS && !isOnline) {
      log('[ERROR] Cabeceras no compatibles. Se requiere "id_venta" (POS) o "id_orden" (Online).', 'error');
      return;
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ TRANSMITIENDO...';
    log(`[CSV] Iniciando ingesta por lotes de ${lines.length - 1} transacciones...`, 'warn');

    let processedCount = 0;
    let successCount = 0;
    let errorCount = 0;

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',').map(c => c.trim());
      if (cols.length !== headers.length) continue;

      let payload = null;
      if (isPOS) {
        const id_venta = cols[headers.indexOf('id_venta')];
        const fecha = cols[headers.indexOf('fecha')];
        const id_cliente = cols[headers.indexOf('id_cliente')];
        const id_producto = cols[headers.indexOf('id_producto')];
        const cantidad = parseFloat(cols[headers.indexOf('cantidad')]);
        const precio_u = parseFloat(cols[headers.indexOf('precio_unitario')]);
        const tienda = cols[headers.indexOf('tienda')];
        
        payload = {
          id: `POS-${id_venta}`,
          data: {
            sku: id_producto,
            canal: "tienda_fisica",
            cliente: id_cliente,
            precio: cantidad * precio_u,
            timestamp: `${fecha}T12:00:00.000Z`,
            nodo: `dashboard-cliente-csv-uploader`
          }
        };
      } else if (isOnline) {
        const id_orden = cols[headers.indexOf('id_orden')];
        const fecha = cols[headers.indexOf('fecha')];
        const id_cliente = cols[headers.indexOf('id_cliente')];
        const total = parseFloat(cols[headers.indexOf('total')]);
        const canal = cols[headers.indexOf('canal')];

        payload = {
          id: `WEB-${id_orden}`,
          data: {
            sku: "Desconocido",
            canal: canal,
            cliente: id_cliente,
            precio: total,
            timestamp: `${fecha}T12:00:00.000Z`,
            nodo: `dashboard-cliente-csv-uploader`
          }
        };
      }

      if (payload) {
        stats.total++;
        try {
          const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          if (res.ok) {
            stats.ok++;
            successCount++;
          } else {
            stats.err++;
            errorCount++;
          }
        } catch (err) {
          stats.err++;
          errorCount++;
        }
        processedCount++;
        updateStats();
      }
    }

    log(`[SUCCESS] Ingesta CSV finalizada. Procesados: ${processedCount} | Éxito: ${successCount} | Errores: ${errorCount}`, 'success');
    uploadBtn.textContent = '⚡ PROCESAR Y ENVIAR';
    uploadBtn.disabled = false;
    fileInput.value = '';
    statusDiv.textContent = 'Ningún archivo cargado.';
    statusDiv.style.color = '';
  };

  reader.readAsText(file);
});
