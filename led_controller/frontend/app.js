const state = {
  devices: [],
  scenes: [],
  macros: [],
};

const api = {
  async get(path) {
    const res = await fetch(path, { method: 'GET' });
    return res.json();
  },
  async post(path, payload = {}) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },
  async del(path) {
    const res = await fetch(path, { method: 'DELETE' });
    return res.json();
  },
};

function setView(viewName) {
  document.querySelectorAll('.nav-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.view === viewName);
  });
  document.querySelectorAll('.view-panel').forEach((panel) => {
    panel.classList.toggle('hidden', panel.id !== viewName);
    panel.classList.toggle('active', panel.id === viewName);
  });
}

document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => setView(btn.dataset.view));
});

function renderDevices(devices) {
  const list = document.getElementById('deviceList');
  if (!list) return;
  list.innerHTML = devices.length
    ? devices.map((device) => `
      <div class="device-card">
        <div class="flex justify-between items-center">
          <div>
            <div class="font-semibold">${device.name || 'Unknown'}</div>
            <div class="text-xs text-slate-400">${device.protocol || 'unknown'} · ${device.mac || 'n/a'}</div>
          </div>
          <button class="primary-btn small" data-mac="${device.mac}" data-name="${device.name}">Connect</button>
        </div>
      </div>`).join('')
    : '<div class="text-slate-400">No devices found.</div>';

  list.querySelectorAll('button[data-mac]').forEach((button) => {
    button.addEventListener('click', async () => {
      const payload = { mac: button.dataset.mac, name: button.dataset.name };
      const res = await api.post('/api/connect', payload);
      console.log('Connected', res);
    });
  });
}

function renderEffects() {
  const grid = document.getElementById('effectsGrid');
  if (!grid) return;
  const effects = Array.from({ length: 22 }, (_, index) => index);
  grid.innerHTML = effects.map((effect) => `
    <button class="effect-btn" data-effect="${effect}">${effect + 1}</button>
  `).join('');

  grid.querySelectorAll('.effect-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.post('/api/effect', { value: Number(button.dataset.effect) });
    });
  });
}

async function loadScenes() {
  const scenes = await api.get('/api/scenes');
  state.scenes = scenes;
  const list = document.getElementById('sceneList');
  list.innerHTML = scenes.map((scene) => `
    <div class="scene-card">
      <div class="font-semibold">${scene.name}</div>
      <div class="text-xs text-slate-400">${scene.r}, ${scene.g}, ${scene.b}</div>
      <div class="mt-2 flex gap-2">
        <button class="primary-btn small" data-apply="${scene.id}">Apply</button>
        <button class="secondary-btn small" data-del="${scene.id}">Delete</button>
      </div>
    </div>
  `).join('');

  list.querySelectorAll('[data-apply]').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.post(`/api/scenes/${button.dataset.apply}/apply`);
    });
  });
  list.querySelectorAll('[data-del]').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.del(`/api/scenes/${button.dataset.del}`);
      await loadScenes();
    });
  });
}

async function loadMacros() {
  const macros = await api.get('/api/macros');
  state.macros = macros;
  const list = document.getElementById('macroList');
  list.innerHTML = macros.map((macro) => `
    <div class="macro-card">
      <div class="flex justify-between items-center">
        <span>${macro.name}</span>
        <div class="flex gap-2">
          <button class="primary-btn small" data-play="${macro.id}">Play</button>
          <button class="secondary-btn small" data-stop="${macro.id}">Stop</button>
        </div>
      </div>
    </div>
  `).join('');

  list.querySelectorAll('[data-play]').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.post(`/api/macros/${button.dataset.play}/play`);
    });
  });
  list.querySelectorAll('[data-stop]').forEach((button) => {
    button.addEventListener('click', async () => {
      await api.post(`/api/macros/${button.dataset.stop}/stop`);
    });
  });
}

document.getElementById('scanBtn')?.addEventListener('click', async () => {
  const devices = await api.post('/api/scan');
  state.devices = devices;
  renderDevices(devices);
});

document.getElementById('colorPicker')?.addEventListener('input', async (event) => {
  const hex = event.target.value;
  const numeric = hex.replace('#', '');
  const r = parseInt(numeric.substring(0, 2), 16);
  const g = parseInt(numeric.substring(2, 4), 16);
  const b = parseInt(numeric.substring(4, 6), 16);
  await api.post('/api/color', { r, g, b });
});

document.getElementById('brightness')?.addEventListener('input', async (event) => {
  await api.post('/api/brightness', { value: Number(event.target.value) });
});

document.getElementById('speed')?.addEventListener('input', async (event) => {
  await api.post('/api/speed', { value: Number(event.target.value) });
});

document.getElementById('colorTemp')?.addEventListener('input', async (event) => {
  await api.post('/api/color_temp', { value: Number(event.target.value) });
});

document.getElementById('powerBtn')?.addEventListener('click', async () => {
  const enabled = document.getElementById('powerBtn').textContent.includes('ON');
  document.getElementById('powerBtn').textContent = enabled ? 'Power OFF' : 'Power ON';
  await api.post('/api/power', { on: !enabled });
});

document.getElementById('musicBtn')?.addEventListener('click', async () => {
  const element = document.getElementById('musicBtn');
  const enabled = !element.classList.contains('is-on');
  element.classList.toggle('is-on', enabled);
  await api.post('/api/music_sync', { enabled });
});

document.getElementById('sendHexBtn')?.addEventListener('click', async () => {
  const value = document.getElementById('hexInput').value;
  const log = document.getElementById('protocolLog');
  const result = await api.post('/api/raw', { hex: value });
  log.textContent = JSON.stringify(result, null, 2);
});

renderEffects();
loadScenes();
loadMacros();
api.get('/api/devices').then((devices) => {
  state.devices = devices;
  renderDevices(devices);
});
