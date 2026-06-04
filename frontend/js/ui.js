/**
 * ui.js
 * Pure UI layer — no business logic.
 * All DOM reads/writes go through this module.
 */

const AGENT_STYLES = {
  supervisor: { bg: 'rgba(0,212,170,0.1)', color: '#00d4aa', label: 'SUPERVISOR' },
  search:     { bg: 'rgba(77,158,255,0.1)',  color: '#4d9eff', label: 'SEARCH'     },
  critic:     { bg: 'rgba(255,107,107,0.1)', color: '#ff6b6b', label: 'CRITIC'     },
  writer:     { bg: 'rgba(245,166,35,0.1)',  color: '#f5a623', label: 'WRITER'     },
  system:     { bg: 'rgba(255,255,255,0.05)',color: '#6b7a8d', label: 'SYS'        },
};

// ── Internal state ────────────────────────────────────────
let _logCount  = 0;
let _startTime = null;
let _timerInterval = null;

// ── Helpers ───────────────────────────────────────────────
function el(id) { return document.getElementById(id); }

function elapsed() {
  if (!_startTime) return '0s';
  return Math.floor((Date.now() - _startTime) / 1000) + 's';
}

// ── Exports ───────────────────────────────────────────────
export function showMainPanel() {
  el('mainPanel').classList.add('visible');
}

export function resetUI() {
  _logCount = 0;
  el('logBody').innerHTML = '';
  el('logCount').textContent = '0 events';
  el('metricIterations').textContent = '0';
  el('metricMessages').textContent   = '0';
  el('metricTokens').textContent     = '0';
  el('metricTime').textContent       = '0s';
  el('iterLabel').textContent        = '0 / 5 max';
  el('resultSection').style.display  = 'none';
  el('resultText').innerHTML         = '';

  for (let i = 0; i < 5; i++) {
    const d = el(`idot-${i}`);
    if (d) { d.className = 'iter-dot'; }
  }

  ['supervisor', 'search', 'critic', 'writer'].forEach(a => {
    setNodeState(a, 'idle');
    setLegendActive(a, false);
    el('iter-' + a).textContent = '';
  });
}

export function startTimer() {
  _startTime = Date.now();
  _timerInterval = setInterval(() => {
    el('metricTime').textContent = elapsed();
  }, 500);
}

export function stopTimer() {
  clearInterval(_timerInterval);
  el('metricTime').textContent = elapsed();
}

export function addLog(agent, message, thinking = false) {
  _logCount++;
  el('logCount').textContent = _logCount + ' events';
  el('metricMessages').textContent = _logCount;

  const body = el('logBody');
  const entry = document.createElement('div');
  entry.className = 'log-entry';

  const s = AGENT_STYLES[agent] || AGENT_STYLES.system;
  entry.innerHTML = `
    <span class="log-agent-tag" style="background:${s.bg};color:${s.color}">${s.label}</span>
    <div class="log-message${thinking ? ' thinking' : ''}">${message}</div>
    <span class="log-time">${elapsed()}</span>
  `;

  body.appendChild(entry);
  body.scrollTop = body.scrollHeight;
}

export function setNodeState(node, state, iterText = '') {
  const nodeEl  = el('node-' + node);
  const statusEl = el('status-' + node);
  const iterEl   = el('iter-' + node);
  if (!nodeEl) return;

  nodeEl.className = 'pipeline-node';
  if (state === 'active') nodeEl.classList.add('active');
  else if (state === 'done')  nodeEl.classList.add('done');
  else if (state === 'error') nodeEl.classList.add('error');

  if (statusEl) statusEl.textContent = state;
  if (iterEl && iterText) iterEl.textContent = iterText;
}

export function setLegendActive(agent, active) {
  const legendEl = el('legend-' + agent);
  if (!legendEl) return;
  if (active) legendEl.classList.add('active-agent');
  else legendEl.classList.remove('active-agent');
}

export function updateIteration(n) {
  el('metricIterations').textContent = n;
  el('iterLabel').textContent = `${n} / 5 max`;
  for (let i = 0; i < 5; i++) {
    const dot = el(`idot-${i}`);
    if (!dot) continue;
    dot.className = 'iter-dot';
    if (i < n)      dot.classList.add('done');
    else if (i === n) dot.classList.add('active');
  }
}

export function updateTokens(n) {
  el('metricTokens').textContent = n;
}

export function setRunButton(state) {
  const btn = el('runBtn');
  if (state === 'loading') {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div> Running...';
  } else {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">▶</span> Run Again';
  }
}

export function renderReport(markdown) {
  el('resultSection').style.display = 'block';

  let html = markdown
    .replace(/^## (.+)$/gm,   '<h2>$1</h2>')
    .replace(/^### (.+)$/gm,  '<h3>$1</h3>')
    .replace(/^# (.+)$/gm,    '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    .replace(/`(.+?)`/g,       '<code>$1</code>')
    .replace(/^> (.+)$/gm,     '<blockquote>$1</blockquote>')
    .replace(/^- (.+)$/gm,     '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>');

  html = html.replace(/<p><\/p>/g, '')
             .replace(/<p>(<h[23])/g, '$1')
             .replace(/(<\/h[23]>)<\/p>/g, '$1');

  el('resultText').innerHTML = html;
  el('resultSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
