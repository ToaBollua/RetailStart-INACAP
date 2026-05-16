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
