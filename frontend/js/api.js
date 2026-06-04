/**
 * api.js
 * Handles all communication with the FastAPI backend.
 * Uses the Fetch API with Server-Sent Events (SSE) for real-time streaming.
 */

const API_BASE = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:8000'
  : '';   // same origin in production

/**
 * Stream research orchestration events from the backend.
 *
 * @param {string} query     - Research topic
 * @param {string} apiKey    - Gemini API key (optional if set in backend .env)
 * @param {function} onEvent - Callback for each AgentEvent object
 * @param {function} onDone  - Called when stream ends
 * @param {function} onError - Called on error
 */
export async function streamResearch({ query, apiKey, onEvent, onDone, onError }) {
  try {
    const response = await fetch(`${API_BASE}/api/v1/research/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, api_key: apiKey || null }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line in buffer

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const raw = line.slice(6).trim();
        if (raw === '[DONE]') { onDone(); return; }
        try {
          const event = JSON.parse(raw);
          onEvent(event);
        } catch {
          // skip malformed lines
        }
      }
    }

    onDone();
  } catch (err) {
    onError(err);
  }
}

/**
 * Health check.
 */
export async function healthCheck() {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  return res.json();
}
