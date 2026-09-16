const WORKER_URL = '__CHAT_WORKER_URL__';

const GREETING = "Hi, I'm BioAzure's product assistant. Tell me what you're looking for — your application, sample type, or testing need — and I'll recommend the right product.";

function createChatWidget() {
  const container = document.getElementById('chat-widget');
  if (!container) return;

  let isOpen = false;
  let messages = [];

  try {
    const saved = sessionStorage.getItem('bioazure-chat');
    if (saved) messages = JSON.parse(saved);
  } catch {}

  if (messages.length === 0) {
    messages = [{ role: 'assistant', content: GREETING }];
  }

  function save() {
    try { sessionStorage.setItem('bioazure-chat', JSON.stringify(messages)); } catch {}
  }

  function render() {
    container.innerHTML = isOpen ? renderPanel() : renderButton();
    if (isOpen) {
      const log = container.querySelector('#chat-log');
      if (log) log.scrollTop = log.scrollHeight;
      container.querySelector('#chat-input')?.focus();
    }
    bindEvents();
  }

  function renderButton() {
    return `<button id="chat-toggle" class="chat-fab" aria-label="Open product finder chat">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
    </button>`;
  }

  function renderPanel() {
    const msgHtml = messages.map(m =>
      `<div class="chat-msg chat-msg-${m.role}">${escapeHtml(m.content)}</div>`
    ).join('');

    return `<div class="chat-panel">
      <div class="chat-header">
        <span>Product Finder</span>
        <button id="chat-close" aria-label="Close chat">&times;</button>
      </div>
      <div id="chat-log" class="chat-log">${msgHtml}</div>
      <form id="chat-form" class="chat-form">
        <input id="chat-input" type="text" placeholder="Describe what you need..." autocomplete="off" />
        <button type="submit">Send</button>
      </form>
    </div>`;
  }

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function bindEvents() {
    container.querySelector('#chat-toggle')?.addEventListener('click', () => { isOpen = true; render(); });
    container.querySelector('#chat-close')?.addEventListener('click', () => { isOpen = false; render(); });
    container.querySelector('#chat-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = container.querySelector('#chat-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      messages.push({ role: 'user', content: text });
      save();
      render();

      try {
        const res = await fetch(WORKER_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: messages.slice(-10) }),
        });
        const data = await res.json();
        messages.push({ role: 'assistant', content: data.reply || 'Sorry, something went wrong. Please try again.' });
      } catch {
        messages.push({ role: 'assistant', content: "I'm having trouble connecting. Please try again or contact us at info@bioazure.com." });
      }
      save();
      render();
    });
  }

  render();

  document.getElementById('open-chat-from-products')?.addEventListener('click', () => {
    isOpen = true;
    render();
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createChatWidget);
} else {
  createChatWidget();
}
