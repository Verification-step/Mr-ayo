const hud = document.getElementById('hud');
const status = document.getElementById('status');
const text = document.getElementById('text');

const ws = new WebSocket('ws://127.0.0.1:8765');
ws.onopen = () => setState('idle', 'Ready', 'Listening for commands');
ws.onmessage = (event) => {
  const m = JSON.parse(event.data);
  if (m.type === 'state') setState(m.state, m.label, m.text || '');
  if (m.type === 'reply') setState('speaking', 'Speaking', m.text);
};
ws.onerror = () => setState('error', 'Engine offline', 'Start the Python engine first');

function setState(state, label, message) {
  hud.className = state;
  status.textContent = label;
  text.textContent = message;
}

window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && e.ctrlKey) {
    e.preventDefault();
    ws.send(JSON.stringify({ type: 'listen_once' }));
  }
});
