import { setupWorker } from 'msw/browser';
import { handlers } from './handlers.js';
import { createRunner } from './stream.mjs';

// Production safety guard: fail closed.
const isExplicitOptIn = new URLSearchParams(window.location.search).get('mock') === '1';
const isDev = import.meta.env?.DEV ?? true;
const enableMocking = isDev && isExplicitOptIn;

const mswStatusEl = document.getElementById('msw-status');
const statusEl = document.getElementById('status');
const runIdEl = document.getElementById('run-id');
const recordsEl = document.getElementById('records');
const errorBoxEl = document.getElementById('error-box');

if (!enableMocking) {
  mswStatusEl.textContent = 'Mocks disabled (enable with ?mock=1 in development)';
}

async function startMsw() {
  if (!enableMocking) return;
  const worker = setupWorker(...handlers);
  await worker.start({ onUnhandledRequest: 'bypass' });
  const res = await fetch('/api/health').then(r => r.json());
  mswStatusEl.textContent = `Active (${res.mockEngine}, synthetic=${res.synthetic})`;
}

startMsw().catch(err => {
  mswStatusEl.textContent = `MSW init error: ${err.message}`;
});

function render(state) {
  statusEl.textContent = state.status;
  runIdEl.textContent = state.runId;
  errorBoxEl.textContent = state.error || '';
  if (!state.rows || state.rows.length === 0) {
    recordsEl.innerHTML = '<em>No records loaded.</em>';
    return;
  }
  recordsEl.innerHTML = state.rows.map(r => `
    <div class="row">
      <span>#${r.id}</span>
      <span>Val: ${r.value}</span>
      <span style="color:#f59e0b;">[SYNTHETIC]</span>
    </div>
  `).join('');
}

const runner = createRunner(render);

document.getElementById('btn-fetch-seed').addEventListener('click', async () => {
  try {
    const data = await fetch('/api/seed').then(r => r.json());
    document.getElementById('seed').value = data.seed;
    document.getElementById('count').value = data.count;
    statusEl.textContent = 'Seed updated via MSW';
  } catch (e) {
    errorBoxEl.textContent = `Fetch error: ${e.message}`;
  }
});

function getParams() {
  return {
    seed: parseInt(document.getElementById('seed').value, 10),
    count: parseInt(document.getElementById('count').value, 10),
    scenario: document.getElementById('scenario').value,
    delay: 35
  };
}

document.getElementById('btn-start').addEventListener('click', () => {
  runner.run(getParams());
});

document.getElementById('btn-reset').addEventListener('click', () => {
  runner.reset(getParams());
});

document.getElementById('btn-abort').addEventListener('click', () => {
  runner.cancel();
});
