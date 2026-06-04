/**
 * main.js
 * Orchestration controller.
 * Connects the API stream to the UI state machine.
 */

import { streamResearch } from './api.js';
import {
  showMainPanel, resetUI, startTimer, stopTimer,
  addLog, setNodeState, setLegendActive,
  updateIteration, updateTokens, setRunButton, renderReport,
} from './ui.js';

// ── Persisted report ──────────────────────────────────────
let finalReportText = '';

// ── Hint chips ────────────────────────────────────────────
export function setQuery(q) {
  document.getElementById('query').value = q;
  document.getElementById('query').focus();
}
window.setQuery = setQuery;

// ── Copy / Download ───────────────────────────────────────
window.copyResult = function () {
  navigator.clipboard.writeText(finalReportText).then(() => {
    const btn = document.querySelector('.result-actions .icon-btn');
    btn.style.color = 'var(--supervisor)';
    setTimeout(() => btn.style.color = '', 1500);
  });
};

window.downloadResult = function () {
  const query = document.getElementById('query').value.trim();
  const blob = new Blob([finalReportText], { type: 'text/markdown' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'research-' + query.slice(0, 30).replace(/\s+/g, '-').toLowerCase() + '.md';
  a.click();
  URL.revokeObjectURL(url);
};

// ── Event handler ─────────────────────────────────────────
function handleEvent(event) {
  const { agent, type, message, thinking, data } = event;

  if (type === 'log') {
    addLog(agent, message, thinking);
  }

  if (type === 'status') {
    const state = message; // 'active' | 'done' | 'error' | 'idle'
    setNodeState(agent, state, data?.label || '');
    setLegendActive(agent, state === 'active');
  }

  if (type === 'metric' && data) {
    if (data.iteration !== undefined) updateIteration(data.iteration);
    if (data.tokens    !== undefined) updateTokens(data.tokens);
  }

  if (type === 'result' && data) {
    finalReportText = data.report || '';
    renderReport(finalReportText);
  }
}

// ── Main run ──────────────────────────────────────────────
window.runOrchestration = async function () {
  const query  = document.getElementById('query').value.trim();
  const apiKey = document.getElementById('apikey').value.trim();

  if (!query) { alert('Please enter a research topic.'); return; }

  setRunButton('loading');
  showMainPanel();
  resetUI();
  startTimer();

  await streamResearch({
    query,
    apiKey,
    onEvent: handleEvent,
    onDone: () => {
      stopTimer();
      setRunButton('idle');
    },
    onError: (err) => {
      addLog('system', `Error: ${err.message}`);
      stopTimer();
      setRunButton('idle');
      ['supervisor', 'search', 'critic', 'writer'].forEach(a => setLegendActive(a, false));
    },
  });
};
