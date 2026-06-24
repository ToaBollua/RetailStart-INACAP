const API_URL = 'http://localhost:8000/ingest';
const API_HEALTH = 'http://localhost:8000/buffer';

let stats = { total: 0, ok: 0, err: 0 };
let selectedCanal = 'web';
let txRows = [];
let txRowCount = 0;

// ─── CLOCK ─────────────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    `[ ${now.toLocaleDateString('es-CL')} ${now.toTimeString().slice(0, 8)} ]`;
}
setInterval(updateClock, 1000);
updateClock();

// ─── API HEALTH CHECK ───────────────────────────────────────────────────────
async function checkApiHealth() {
  const el = document.getElementById('api-status');
  try {
    const res = await fetch(API_HEALTH, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      el.textContent = `OK (buf: ${data.buffer_size ?? 0})`;
      el.style.color = 'var(--neon)';
    } else {
      el.textContent = `HTTP ${res.status}`;
      el.style.color = 'var(--red)';
    }
  } catch {
    el.textContent = 'OFFLINE';
    el.style.color = 'var(--red)';
  }
}
setInterval(checkApiHealth, 5000);
checkApiHealth();

// ─── CANAL SELECTOR ─────────────────────────────────────────────────────────
document.querySelectorAll('.canal-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    selectedCanal = btn.dataset.canal;
    document.getElementById('canal').value = selectedCanal;
    document.querySelectorAll('.canal-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});
document.querySelector('[data-canal="web"]').click();

// ─── LOGGER ─────────────────────────────────────────────────────────────────
function log(msg, type = 'info') {
  const terminal = document.getElementById('log-terminal');
  const entry = document.createElement('div');
  entry.classList.add('log-entry');
  const ts = new Date().toTimeString().slice(0, 8);
  const palette = {
    info:    'color:var(--text-dim)',
    success: 'color:var(--neon);text-shadow:0 0 6px rgba(0,255,65,0.5)',
    error:   'color:var(--red)',
    tx:      'color:var(--yellow)',
    warn:    'color:#aaff00',
  };
  entry.style.cssText = palette[type] || palette.info;
  entry.textContent = `[${ts}] ${msg}`;
  terminal.appendChild(entry);
  terminal.scrollTop = terminal.scrollHeight;
}

// ─── STATS UPDATE ────────────────────────────────────────────────────────────
function updateStats() {
  document.getElementById('stat-total').textContent = stats.total;
  document.getElementById('stat-ok').textContent    = stats.ok;
  document.getElementById('stat-err').textContent   = stats.err;
}

// ─── TABLE ROW INSERT ────────────────────────────────────────────────────────
function addTableRow(txData, status) {
  txRowCount++;
  const tbody = document.getElementById('tx-tbody');
  const empty = document.getElementById('empty-state');
  empty.style.display = 'none';

  const tr = document.createElement('tr');
  const ts = txData.timestamp
    ? txData.timestamp.replace('T', ' ').slice(0, 19)
    : new Date().toISOString().replace('T', ' ').slice(0, 19);

  const canalClass = (txData.canal || '').replace('_', '-');
  const statusClass = status === 'ok' ? 'ok' : 'err';
  const statusIcon  = status === 'ok' ? '✓ OK' : '✗ ERR';
  const precio = parseFloat(txData.precio || 0).toLocaleString('es-CL');

  tr.innerHTML = `
    <td class="td-id">${txRowCount}</td>
    <td class="td-id">${txData.id || '—'}</td>
    <td class="td-ts">${ts}</td>
    <td>${txData.cliente || '—'}</td>
    <td>${txData.sku || '—'}</td>
    <td><span class="td-canal ${canalClass}">${txData.canal || '—'}</span></td>
    <td class="td-precio">$${precio}</td>
    <td class="td-status ${statusClass}">${statusIcon}</td>
  `;

  // newest rows at top
  tbody.insertBefore(tr, tbody.firstChild);
  document.getElementById('tx-count').textContent = `${txRowCount} registros`;
}

// ─── CLEAR LOG ───────────────────────────────────────────────────────────────
document.getElementById('btn-clear').addEventListener('click', () => {
  document.getElementById('log-terminal').innerHTML = '';
  log('Terminal limpiada por el operador.', 'warn');
});

// ─── RESET TABLE ─────────────────────────────────────────────────────────────
document.getElementById('btn-clear-table').addEventListener('click', () => {
  document.getElementById('tx-tbody').innerHTML = '';
  document.getElementById('empty-state').style.display = 'flex';
  document.getElementById('tx-count').textContent = '0 registros';
  txRowCount = 0;
  stats = { total: 0, ok: 0, err: 0 };
  updateStats();
  log('Tabla y contadores reseteados por el operador.', 'warn');
});

// ─── SEND TRANSACTION ────────────────────────────────────────────────────────
async function sendTransaction(payload) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

document.getElementById('btn-transact').addEventListener('click', async () => {
  const sku     = document.getElementById('sku').value;
  const canal   = selectedCanal;
  const cliente = document.getElementById('cliente').value;
  const precio  = parseFloat(document.getElementById('precio').value);
  const txId    = `TX-${Date.now().toString(16).toUpperCase()}`;

  const payload = {
    id: txId,
    data: { sku, canal, cliente, precio, timestamp: new Date().toISOString(), nodo: 'dashboard-cliente-v2' }
  };

  stats.total++;
  updateStats();

  const btn = document.getElementById('btn-transact');
  btn.disabled = true;
  btn.textContent = '⏳ Procesando...';

  log(`TX init → ${txId} | ${sku} | ${canal} | ${cliente} | $${precio.toLocaleString('es-CL')}`, 'info');

  try {
    const json = await sendTransaction(payload);
    stats.ok++;
    log(`[OK] ${txId} → Data Lake. Buffer: ${json.buffer_size} en cola.`, 'success');
    addTableRow({ ...payload.data, id: txId }, 'ok');
  } catch (err) {
    stats.err++;
    log(`[ERR] ${txId} → ${err.message}`, 'error');
    addTableRow({ ...payload.data, id: txId }, 'err');
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ Ejecutar Transacción';
    updateStats();
  }
});

// ─── CSV UPLOAD ───────────────────────────────────────────────────────────────
const fileInput = document.getElementById('csv-file');
const selectBtn = document.getElementById('btn-select-file');
const uploadBtn = document.getElementById('btn-upload-csv');
const statusDiv = document.getElementById('file-status');
const progressWrap = document.getElementById('progress-wrap');
const progressFill = document.getElementById('progress-fill');
const progressLabel = document.getElementById('progress-label');

selectBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    statusDiv.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    statusDiv.style.color = 'var(--neon)';
    uploadBtn.disabled = false;
    log(`[CSV] Archivo listo: ${file.name}`, 'tx');
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
      log('[ERR] Archivo vacío o sin datos.', 'error');
      return;
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const isPOS    = headers.includes('id_venta');
    const isOnline = headers.includes('id_orden');

    if (!isPOS && !isOnline) {
      log('[ERR] Cabeceras inválidas. Se requiere "id_venta" (POS) o "id_orden" (Online).', 'error');
      return;
    }

    const totalRows = lines.length - 1;
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Transmitiendo...';
    progressWrap.classList.add('active');
    log(`[CSV] Tipo detectado: ${isPOS ? 'POS (tienda física)' : 'Online (web/app)'}`, 'tx');
    log(`[CSV] Iniciando ingesta de ${totalRows} transacciones...`, 'warn');

    let processed = 0, success = 0, errors = 0;

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',').map(c => c.trim());
      if (cols.length !== headers.length) continue;

      let txData = null;

      if (isPOS) {
        const id_venta  = cols[headers.indexOf('id_venta')];
        const fecha     = cols[headers.indexOf('fecha')];
        const id_cli    = cols[headers.indexOf('id_cliente')];
        const id_prod   = cols[headers.indexOf('id_producto')];
        const cantidad  = parseFloat(cols[headers.indexOf('cantidad')]);
        const precio_u  = parseFloat(cols[headers.indexOf('precio_unitario')]);
        txData = {
          id: `POS-${id_venta}`,
          sku: id_prod, canal: 'tienda_fisica', cliente: id_cli,
          precio: cantidad * precio_u,
          timestamp: `${fecha}T12:00:00.000Z`,
        };
      } else {
        const id_orden = cols[headers.indexOf('id_orden')];
        const fecha    = cols[headers.indexOf('fecha')];
        const id_cli   = cols[headers.indexOf('id_cliente')];
        const total    = parseFloat(cols[headers.indexOf('total')]);
        const canal    = cols[headers.indexOf('canal')];
        txData = {
          id: `WEB-${id_orden}`,
          sku: 'N/A', canal, cliente: id_cli,
          precio: total,
          timestamp: `${fecha}T12:00:00.000Z`,
        };
      }

      stats.total++;
      try {
        await sendTransaction({ id: txData.id, data: { sku: txData.sku, canal: txData.canal, cliente: txData.cliente, precio: txData.precio, timestamp: txData.timestamp, nodo: 'csv-uploader-v2' } });
        stats.ok++;
        success++;
        addTableRow(txData, 'ok');
        log(`[OK] ${txData.id} | ${txData.cliente} | $${parseFloat(txData.precio).toLocaleString('es-CL')}`, 'success');
      } catch (err) {
        stats.err++;
        errors++;
        addTableRow(txData, 'err');
        log(`[ERR] ${txData.id} → ${err.message}`, 'error');
      }

      processed++;
      const pct = Math.round((processed / totalRows) * 100);
      progressFill.style.width = `${pct}%`;
      progressLabel.textContent = `${processed} / ${totalRows} transacciones (${pct}%)`;
      updateStats();
    }

    log(`[DONE] CSV finalizado. ${success} OK | ${errors} ERR de ${processed} filas.`, processed === success ? 'success' : 'warn');
    uploadBtn.textContent = '⚡ Enviar';
    uploadBtn.disabled = false;
    progressWrap.classList.remove('active');
    progressFill.style.width = '0%';
    fileInput.value = '';
    statusDiv.textContent = 'Ningún archivo cargado.';
    statusDiv.style.color = '';
  };

  reader.readAsText(file);
});
