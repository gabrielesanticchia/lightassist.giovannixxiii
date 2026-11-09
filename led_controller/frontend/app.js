const state = {
  devices: [],
  scenes: [],
  macros: [],
  editingMacroId: null,
  macroBlocks: [],
  powerOn: false,
};

const viewTitles = {
  scan: 'Dispositivi',
  control: 'Controlli',
  scenes: 'Scene',
  macro: 'Macro studio',
  protocol: 'Test protocollo',
};

let toastTimer;

const api = {
  async get(path) {
    const res = await fetch(path, { method: 'GET' });
    return readResponse(res);
  },
  async post(path, payload = {}) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return readResponse(res);
  },
  async del(path) {
    const res = await fetch(path, { method: 'DELETE' });
    return readResponse(res);
  },
  async put(path, payload = {}) {
    const res = await fetch(path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return readResponse(res);
  },
};

async function readResponse(response) {
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || `Richiesta non riuscita (${response.status})`);
  }
  return body;
}

function setView(viewName) {
  if (!viewTitles[viewName]) return;
  document.getElementById('pageTitle').textContent = viewTitles[viewName];
  document.querySelectorAll('.nav-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.view === viewName);
  });
  document.querySelectorAll('.view-panel').forEach((panel) => {
    panel.classList.toggle('hidden', panel.id !== viewName);
    panel.classList.toggle('active', panel.id === viewName);
  });
}

function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 2800);
}

function setConnectionStatus(connected, name = '') {
  const status = document.getElementById('connectionStatus');
  if (!status) return;
  status.classList.toggle('connected', connected);
  status.lastElementChild.textContent = connected ? `Connesso${name ? ` · ${name}` : ''}` : 'Non connesso';
}

document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => setView(btn.dataset.view));
});

function renderDevices(devices) {
  const list = document.getElementById('deviceList');
  if (!list) return;
  const count = document.getElementById('deviceCount');
  if (count) count.textContent = `${devices.length} ${devices.length === 1 ? 'dispositivo' : 'dispositivi'}`;
  list.innerHTML = devices.length
    ? devices.map((device) => `
      <div class="device-card">
        <div class="flex justify-between items-center">
          <div>
            <div class="font-semibold">${escapeHtml(device.name || 'Unknown')}</div>
            <div class="text-xs text-slate-400">${escapeHtml(device.protocol || 'unknown')} · ${escapeHtml(device.mac || 'n/a')}</div>
          </div>
          <button class="primary-btn small" data-mac="${escapeHtml(device.mac || '')}" data-name="${escapeHtml(device.name || '')}">Connetti</button>
        </div>
      </div>`).join('')
    : '<div class="text-slate-400">Nessun dispositivo trovato. Premi “Cerca dispositivi” per eseguire una scansione.</div>';

  list.querySelectorAll('button[data-mac]').forEach((button) => {
    button.addEventListener('click', async () => {
      const payload = { mac: button.dataset.mac, name: button.dataset.name };
      button.disabled = true;
      try {
        const res = await api.post('/api/connect', payload);
        setConnectionStatus(true, res.name || payload.name);
        showToast(`Connesso a ${res.name || payload.name}`);
      } catch (error) {
        showToast(`Connessione non riuscita: ${error.message}`);
      } finally {
        button.disabled = false;
      }
    });
  });
}

function renderEffects() {
  const grid = document.getElementById('effectsGrid');
  if (!grid) return;
  const effects = Array.from({ length: 22 }, (_, index) => index);
  grid.innerHTML = effects.map((effect) => `
    <button class="effect-btn" data-effect="${effect}" aria-label="Effetto ${effect + 1}">${effect + 1}</button>
  `).join('');

  grid.querySelectorAll('.effect-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await api.post('/api/effect', { value: Number(button.dataset.effect) });
        grid.querySelectorAll('.effect-btn').forEach((item) => item.classList.toggle('selected', item === button));
      } catch (error) {
        showToast(error.message);
      }
    });
  });
}

async function loadScenes() {
  const scenes = await api.get('/api/scenes');
  state.scenes = scenes;
  const list = document.getElementById('sceneList');
  list.innerHTML = scenes.map((scene) => `
    <div class="scene-card">
      <div class="font-semibold">${escapeHtml(scene.name)}</div>
      <div class="text-xs text-slate-400">${scene.r}, ${scene.g}, ${scene.b}</div>
      <div class="mt-2 flex gap-2">
        <button class="primary-btn small" data-apply="${escapeHtml(scene.id)}">Applica</button>
        <button class="secondary-btn small" data-del="${escapeHtml(scene.id)}">Elimina</button>
      </div>
    </div>
  `).join('') || '<p class="text-slate-400">Non hai ancora salvato scene.</p>';

  list.querySelectorAll('[data-apply]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await api.post(`/api/scenes/${button.dataset.apply}/apply`);
        showToast('Scena applicata.');
      } catch (error) {
        showToast(error.message);
      }
    });
  });
  list.querySelectorAll('[data-del]').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.del(`/api/scenes/${button.dataset.del}`);
      await loadScenes();
      showToast('Scena eliminata.');
    });
  });
}

async function loadMacros() {
  const macros = await api.get('/api/macros');
  state.macros = macros;
  const list = document.getElementById('macroList');
  list.innerHTML = macros.length ? macros.map((macro) => `
    <div class="macro-card">
      <div class="flex justify-between items-center">
        <button class="macro-load-btn" data-load="${macro.id}">${escapeHtml(macro.name)}</button>
        <div class="flex gap-2">
          <button class="primary-btn small" data-play="${macro.id}">Play</button>
          <button class="secondary-btn small" data-stop="${macro.id}">Stop</button>
        </div>
      </div>
    </div>
  `).join('') : '<p class="text-sm text-slate-400">Nessuna macro salvata. Crea la prima con i blocchi.</p>';

  list.querySelectorAll('[data-load]').forEach((button) => {
    button.addEventListener('click', () => {
      const macro = state.macros.find((item) => item.id === button.dataset.load);
      if (macro) loadMacroIntoEditor(macro);
    });
  });
  list.querySelectorAll('[data-play]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await api.post(`/api/macros/${button.dataset.play}/play`);
        setMacroStatus('Macro avviata.');
        showToast('Macro avviata.');
      } catch (error) {
        setMacroStatus(error.message);
        showToast(error.message);
      }
    });
  });
  list.querySelectorAll('[data-stop]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await api.post(`/api/macros/${button.dataset.stop}/stop`);
        setMacroStatus('Macro fermata.');
        showToast('Macro fermata.');
      } catch (error) {
        setMacroStatus(error.message);
        showToast(error.message);
      }
    });
  });
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

function setMacroStatus(message) {
  const status = document.getElementById('macroEditorStatus');
  if (status) status.textContent = message;
}

function makeBlock(type) {
  const id = globalThis.crypto?.randomUUID?.() || `block-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  if (type === 'sleep') return { id, type, duration: 3 };
  if (type === 'flash') return { id, type, from_color: '#ffffff', to_color: '#0000ff', duration: 5, interval: 0.5 };
  return { id, type: 'color', color: '#0000ff', duration: 5 };
}

function renderMacroBlocks() {
  const container = document.getElementById('macroBlocks');
  if (!container) return;
  if (!state.macroBlocks.length) {
    container.innerHTML = '<div class="macro-empty">Aggiungi un blocco qui sopra per iniziare la sequenza.</div>';
    return;
  }

  container.innerHTML = state.macroBlocks.map((block, index) => {
    let controls = '';
    if (block.type === 'color') {
      controls = `Colore <input type="color" data-field="color" value="${escapeHtml(block.color || '#0000ff')}" aria-label="Colore blocco" />
        per <input type="number" data-field="duration" min="0.1" max="3600" step="0.1" value="${escapeHtml(block.duration ?? 5)}" aria-label="Durata in secondi" /> secondi`;
    } else if (block.type === 'sleep') {
      controls = `Attendi <input type="number" data-field="duration" min="0.1" max="3600" step="0.1" value="${escapeHtml(block.duration ?? 3)}" aria-label="Durata in secondi" /> secondi`;
    } else {
      controls = `Flash da <input type="color" data-field="from_color" value="${escapeHtml(block.from_color || '#ffffff')}" aria-label="Colore iniziale" />
        a <input type="color" data-field="to_color" value="${escapeHtml(block.to_color || '#0000ff')}" aria-label="Colore finale" />
        per <input type="number" data-field="duration" min="0.1" max="3600" step="0.1" value="${escapeHtml(block.duration ?? 5)}" aria-label="Durata in secondi" /> secondi,
        ogni <input type="number" data-field="interval" min="0.1" max="10" step="0.1" value="${escapeHtml(block.interval ?? 0.5)}" aria-label="Intervallo flash in secondi" /> s`;
    }

    return `<article class="macro-block" draggable="true" data-type="${escapeHtml(block.type)}" data-block-id="${escapeHtml(block.id)}">
      <div class="macro-block-top">
        <span class="macro-block-type">${block.type === 'color' ? '💡 Colore' : block.type === 'sleep' ? '⏱ Attesa' : '⚡ Flash'}</span>
        <div class="macro-block-actions">
          <button type="button" class="block-move-btn" data-move="-1" data-index="${index}" aria-label="Sposta su" ${index === 0 ? 'disabled' : ''}>↑</button>
          <button type="button" class="block-move-btn" data-move="1" data-index="${index}" aria-label="Sposta giù" ${index === state.macroBlocks.length - 1 ? 'disabled' : ''}>↓</button>
          <button type="button" class="block-remove-btn" data-remove="${block.id}" aria-label="Rimuovi blocco">Rimuovi</button>
        </div>
      </div>
      <div class="macro-block-controls">${controls}</div>
    </article>`;
  }).join('');

  container.querySelectorAll('[data-field]').forEach((input) => {
    input.addEventListener('input', () => {
      const block = state.macroBlocks.find((item) => item.id === input.closest('[data-block-id]').dataset.blockId);
      if (block) block[input.dataset.field] = input.type === 'number' ? Number(input.value) : input.value;
    });
  });
  container.querySelectorAll('[data-remove]').forEach((button) => {
    button.addEventListener('click', () => {
      state.macroBlocks = state.macroBlocks.filter((block) => block.id !== button.dataset.remove);
      renderMacroBlocks();
    });
  });
  container.querySelectorAll('[data-move]').forEach((button) => {
    button.addEventListener('click', () => moveMacroBlock(Number(button.dataset.index), Number(button.dataset.move)));
  });
  container.querySelectorAll('[data-block-id]').forEach((element) => {
    element.addEventListener('dragstart', (event) => {
      event.dataTransfer.setData('text/plain', element.dataset.blockId);
      event.dataTransfer.effectAllowed = 'move';
    });
    element.addEventListener('dragover', (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    });
    element.addEventListener('drop', (event) => {
      event.preventDefault();
      const fromId = event.dataTransfer.getData('text/plain');
      const fromIndex = state.macroBlocks.findIndex((item) => item.id === fromId);
      const toIndex = state.macroBlocks.findIndex((item) => item.id === element.dataset.blockId);
      moveMacroBlock(fromIndex, toIndex - fromIndex);
    });
  });
}

function moveMacroBlock(index, offset) {
  const target = index + offset;
  if (index < 0 || target < 0 || target >= state.macroBlocks.length) return;
  const [block] = state.macroBlocks.splice(index, 1);
  state.macroBlocks.splice(target, 0, block);
  renderMacroBlocks();
}

function loadMacroIntoEditor(macro) {
  state.editingMacroId = macro.id;
  document.getElementById('macroName').value = macro.name || '';
  state.macroBlocks = (macro.steps || []).map((block) => {
    const legacyColor = block.r !== undefined
      ? `#${[block.r, block.g, block.b].map((value) => Number(value).toString(16).padStart(2, '0')).join('')}`
      : '#0000ff';
    const duration = block.duration ?? (block.delay_ms ? Number(block.delay_ms) / 1000 : 5);
    return {
      ...block,
      id: block.id || `block-${Date.now()}-${Math.random().toString(16).slice(2)}`,
      type: block.type || 'color',
      color: block.color || legacyColor,
      duration,
    };
  });
  renderMacroBlocks();
  setMacroStatus(`Modifica di "${macro.name}".`);
}

document.querySelectorAll('[data-add-block]').forEach((button) => {
  button.addEventListener('click', () => {
    state.macroBlocks.push(makeBlock(button.dataset.addBlock));
    renderMacroBlocks();
  });
});

document.getElementById('newMacroBtn')?.addEventListener('click', () => {
  state.editingMacroId = null;
  state.macroBlocks = [];
  document.getElementById('macroName').value = '';
  renderMacroBlocks();
  setMacroStatus('Nuova macro.');
});

document.getElementById('saveMacroBtn')?.addEventListener('click', async () => {
  const name = document.getElementById('macroName').value.trim();
  if (!name) {
    setMacroStatus('Inserisci un nome per la macro.');
    return;
  }
  if (!state.macroBlocks.length) {
    setMacroStatus('Aggiungi almeno un blocco prima di salvare.');
    return;
  }
  const payload = {
    id: state.editingMacroId || (globalThis.crypto?.randomUUID?.() || `macro-${Date.now()}`),
    name,
    steps: state.macroBlocks.map(({ id, ...block }) => block),
    loop: false,
  };
  try {
    if (state.editingMacroId) await api.put(`/api/macros/${state.editingMacroId}`, payload);
    else await api.post('/api/macros', payload);
    state.editingMacroId = payload.id;
    await loadMacros();
    setMacroStatus('Macro salvata.');
  } catch (error) {
    setMacroStatus(`Errore nel salvataggio: ${error.message}`);
  }
});

document.getElementById('scanBtn')?.addEventListener('click', async () => {
  const button = document.getElementById('scanBtn');
  button.disabled = true;
  button.innerHTML = '<span class="scan-spinner" aria-hidden="true"></span> Ricerca in corso';
  try {
    const devices = await api.post('/api/scan');
    state.devices = devices;
    renderDevices(devices);
    showToast(devices.length ? `Trovati ${devices.length} dispositivi.` : 'Nessun dispositivo trovato.');
  } catch (error) {
    showToast(`Scansione non riuscita: ${error.message}`);
  } finally {
    button.disabled = false;
    button.innerHTML = '<span aria-hidden="true">⌕</span> Cerca dispositivi';
  }
});

document.getElementById('colorPicker')?.addEventListener('input', async (event) => {
  const hex = event.target.value;
  const numeric = hex.replace('#', '');
  const r = parseInt(numeric.substring(0, 2), 16);
  const g = parseInt(numeric.substring(2, 4), 16);
  const b = parseInt(numeric.substring(4, 6), 16);
  document.getElementById('colorPreview').style.background = hex;
  document.getElementById('colorHexLabel').textContent = hex.toUpperCase();
  try { await api.post('/api/color', { r, g, b }); } catch (error) { showToast(error.message); }
});

document.getElementById('brightness')?.addEventListener('input', async (event) => {
  document.getElementById('brightnessValue').value = event.target.value;
  try { await api.post('/api/brightness', { value: Number(event.target.value) }); } catch (error) { showToast(error.message); }
});

document.getElementById('speed')?.addEventListener('input', async (event) => {
  document.getElementById('speedValue').value = event.target.value;
  try { await api.post('/api/speed', { value: Number(event.target.value) }); } catch (error) { showToast(error.message); }
});

document.getElementById('colorTemp')?.addEventListener('input', async (event) => {
  document.getElementById('colorTempValue').value = event.target.value;
  try { await api.post('/api/color_temp', { value: Number(event.target.value) }); } catch (error) { showToast(error.message); }
});

document.getElementById('powerBtn')?.addEventListener('click', async () => {
  const button = document.getElementById('powerBtn');
  const enabled = !state.powerOn;
  try {
    await api.post('/api/power', { on: enabled });
    state.powerOn = enabled;
    button.innerHTML = `<span class="power-glyph">⏻</span> ${enabled ? 'Spegni' : 'Accendi'}`;
    button.classList.toggle('is-on', enabled);
    showToast(enabled ? 'Luce accesa.' : 'Luce spenta.');
  } catch (error) {
    showToast(error.message);
  }
});

document.getElementById('musicBtn')?.addEventListener('click', async () => {
  const element = document.getElementById('musicBtn');
  const enabled = !element.classList.contains('is-on');
  element.classList.toggle('is-on', enabled);
  try {
    await api.post('/api/music_sync', { enabled });
    showToast(enabled ? 'Music sync attivato.' : 'Music sync disattivato.');
  } catch (error) {
    element.classList.toggle('is-on', !enabled);
    showToast(error.message);
  }
});

document.getElementById('sendHexBtn')?.addEventListener('click', async () => {
  const value = document.getElementById('hexInput').value;
  const log = document.getElementById('protocolLog');
  try {
    const result = await api.post('/api/raw', { hex: value });
    log.textContent = JSON.stringify(result, null, 2);
    showToast('Frame inviato.');
  } catch (error) {
    log.textContent = error.message;
    showToast(error.message);
  }
});

renderEffects();
loadScenes();
loadMacros();
api.get('/api/devices').then((devices) => {
  state.devices = devices;
  renderDevices(devices);
}).catch((error) => showToast(`Impossibile caricare i dispositivi: ${error.message}`));

document.getElementById('macroName')?.addEventListener('input', () => {
  if (state.editingMacroId) setMacroStatus('Modifiche non salvate.');
});
