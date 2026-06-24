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

// ─── CSV MULTI-FILE UPLOAD ────────────────────────────────────────────────────

const fileInput    = document.getElementById('csv-file');
const dropZone     = document.getElementById('drop-zone');
const uploadBtn    = document.getElementById('btn-upload-csv');
const fileQueue    = document.getElementById('file-queue');
const progressWrap = document.getElementById('progress-wrap');
const progressGlobalWrap = document.getElementById('progress-global-wrap');
const progressFill = document.getElementById('progress-fill');
const progressGlobalFill = document.getElementById('progress-global-fill');
const progressLabel = document.getElementById('progress-label');
const progressFileLabel = document.getElementById('progress-file-label');
const progressGlobalLabel = document.getElementById('progress-global-label');

// Cola de archivos en memoria (File objects)
let fileList = [];

// ── Sincronizar botón PROCESAR según si hay archivos en cola ──
function syncUploadBtn() {
  uploadBtn.disabled = fileList.length === 0;
}

// ── Renderizar la cola visual ──
function renderQueue() {
  fileQueue.innerHTML = '';
  fileList.forEach((file, idx) => {
    const item = document.createElement('div');
    item.classList.add('file-item');
    item.id = `fitem-${idx}`;
    item.innerHTML = `
      <span class="file-item-name" title="${file.name}">${file.name}</span>
      <span class="file-item-size">${(file.size / 1024).toFixed(1)}KB</span>
      <span class="file-item-badge" id="fbadge-${idx}">EN COLA</span>
      <button class="file-item-remove" data-idx="${idx}" title="Quitar">✕</button>
    `;
    fileQueue.appendChild(item);
  });

  // Botones de quitar por índice
  fileQueue.querySelectorAll('.file-item-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const i = parseInt(e.currentTarget.dataset.idx);
      fileList.splice(i, 1);
      renderQueue();
      syncUploadBtn();
    });
  });

  syncUploadBtn();
}

// ── Añadir archivos a la cola (sin duplicados por nombre) ──
function addFiles(newFiles) {
  const existingNames = new Set(fileList.map(f => f.name));
  let added = 0;
  for (const f of newFiles) {
    if (f.name.toLowerCase().endsWith('.csv') && !existingNames.has(f.name)) {
      fileList.push(f);
      existingNames.add(f.name);
      added++;
    }
  }
  if (added > 0) {
    log(`[COLA] ${added} archivo(s) añadido(s). Total en cola: ${fileList.length}`, 'tx');
  }
  renderQueue();
}

// ── Click en drop zone → abrir selector ──
dropZone.addEventListener('click', () => fileInput.click());

// ── Selector de archivos (multi) ──
fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) addFiles(fileInput.files);
  fileInput.value = '';  // reset para permitir seleccionar el mismo archivo de nuevo
});

// ── Drag & Drop ──
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const dropped = [...e.dataTransfer.files].filter(f => f.name.toLowerCase().endsWith('.csv'));
  if (dropped.length) addFiles(dropped);
  else log('[WARN] Solo se aceptan archivos .csv', 'warn');
});

// ── Vaciar cola ──
document.getElementById('btn-clear-queue').addEventListener('click', () => {
  fileList = [];
  renderQueue();
  progressWrap.classList.remove('active');
  progressGlobalWrap.classList.remove('active');
  log('[COLA] Cola vaciada.', 'warn');
});

// ── Parser CSV → payload ──
function parseCSVText(text) {
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length <= 1) return null;

  const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
  const isPOS    = headers.includes('id_venta');
  const isOnline = headers.includes('id_orden');
  if (!isPOS && !isOnline) return null;

  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(',').map(c => c.trim());
    if (cols.length !== headers.length) continue;
    if (isPOS) {
      const id_venta = cols[headers.indexOf('id_venta')];
      const fecha    = cols[headers.indexOf('fecha')];
      const id_cli   = cols[headers.indexOf('id_cliente')];
      const id_prod  = cols[headers.indexOf('id_producto')];
      const cantidad = parseFloat(cols[headers.indexOf('cantidad')]);
      const precio_u = parseFloat(cols[headers.indexOf('precio_unitario')]);
      rows.push({ id: `POS-${id_venta}`, sku: id_prod, canal: 'tienda_fisica', cliente: id_cli, precio: cantidad * precio_u, timestamp: `${fecha}T12:00:00.000Z` });
    } else {
      const id_orden = cols[headers.indexOf('id_orden')];
      const fecha    = cols[headers.indexOf('fecha')];
      const id_cli   = cols[headers.indexOf('id_cliente')];
      const total    = parseFloat(cols[headers.indexOf('total')]);
      const canal    = cols[headers.indexOf('canal')];
      rows.push({ id: `WEB-${id_orden}`, sku: 'N/A', canal, cliente: id_cli, precio: total, timestamp: `${fecha}T12:00:00.000Z` });
    }
  }
  return { type: isPOS ? 'POS' : 'ONLINE', rows };
}

// ── Actualizar badge de archivo en la cola ──
function setFileBadge(idx, state) {
  const badge = document.getElementById(`fbadge-${idx}`);
  if (!badge) return;
  badge.className = `file-item-badge ${state}`;
  badge.textContent = state === 'active' ? '↻ PROCESANDO' : state === 'done' ? '✓ LISTO' : state === 'error' ? '✗ ERROR' : 'EN COLA';
}

// ── PROCESAR COLA ──
uploadBtn.addEventListener('click', async () => {
  if (fileList.length === 0) return;

  uploadBtn.disabled = true;
  uploadBtn.textContent = '⏳ Procesando...';
  progressWrap.classList.add('active');
  progressGlobalWrap.classList.add('active');

  const totalFiles = fileList.length;
  let filesProcessed = 0;

  log(`[COLA] Iniciando ingesta de ${totalFiles} archivo(s)...`, 'warn');

  for (let fi = 0; fi < fileList.length; fi++) {
    const file = fileList[fi];
    setFileBadge(fi, 'active');

    // Actualizar progreso global
    progressGlobalFill.style.width = `${Math.round((fi / totalFiles) * 100)}%`;
    progressGlobalLabel.textContent = `Global: ${fi + 1} / ${totalFiles} archivos`;

    // Leer archivo
    const text = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Error leyendo archivo'));
      reader.readAsText(file);
    });

    const parsed = parseCSVText(text);
    if (!parsed) {
      log(`[ERR] ${file.name}: cabeceras inválidas (se requiere id_venta o id_orden). Saltando.`, 'error');
      setFileBadge(fi, 'error');
      filesProcessed++;
      continue;
    }

    const { type, rows } = parsed;
    log(`[CSV] ${file.name} | tipo=${type} | ${rows.length} filas`, 'tx');

    progressFileLabel.textContent = `Archivo: ${file.name}`;
    progressFill.style.width = '0%';
    progressLabel.textContent = `0 / ${rows.length} tx`;

    let processed = 0, success = 0, errors = 0;

    for (const txData of rows) {
      stats.total++;
      try {
        await sendTransaction({ id: txData.id, data: { sku: txData.sku, canal: txData.canal, cliente: txData.cliente, precio: txData.precio, timestamp: txData.timestamp, nodo: 'csv-multi-uploader-v2' } });
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
      const pct = Math.round((processed / rows.length) * 100);
      progressFill.style.width = `${pct}%`;
      progressLabel.textContent = `${processed} / ${rows.length} tx (${pct}%)`;
      updateStats();
    }

    setFileBadge(fi, errors === 0 ? 'done' : 'error');
    log(`[DONE] ${file.name}: ${success} OK | ${errors} ERR`, errors === 0 ? 'success' : 'warn');
    filesProcessed++;
  }

  // Progreso global → 100%
  progressGlobalFill.style.width = '100%';
  progressGlobalLabel.textContent = `Global: ${filesProcessed} / ${totalFiles} archivos completados`;
  progressFileLabel.textContent = 'Ingesta completada.';
  progressFill.style.width = '100%';

  log(`[COLA] Ingesta total finalizada. ${filesProcessed} archivos procesados.`, 'success');
  uploadBtn.textContent = '⚡ PROCESAR COLA';
  uploadBtn.disabled = fileList.length === 0;
});



