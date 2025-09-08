async function send() {
  const input = document.getElementById('input');
  const chatbox = document.getElementById('chatbox');
  const msg = input.value.trim();
  if (!msg) return;

  // Add user message bubble
  chatbox.innerHTML += `<div class="msg user">${msg}</div>`;
  input.value = '';
  chatbox.scrollTop = chatbox.scrollHeight;

  // Add animated loading message
  const loadingMsg = document.createElement('div');
  loadingMsg.className = 'msg bot';
  loadingMsg.id = 'loading';
  loadingMsg.innerHTML = '✨ <em>Gemini is thinking...</em>';
  chatbox.appendChild(loadingMsg);
  chatbox.scrollTop = chatbox.scrollHeight;

  try {
    // Call backend
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });

    const data = await res.json();

    // Remove loading message
    const loadingElem = document.getElementById('loading');
    if (loadingElem) chatbox.removeChild(loadingElem);

    // Add bot reply with fade-in effect
    const botMsg = document.createElement('div');
    botMsg.className = 'msg bot';
    botMsg.style.opacity = 0;
    botMsg.innerHTML = data.reply;
    chatbox.appendChild(botMsg);

    // Animate bot message
    setTimeout(() => {
      botMsg.style.transition = 'opacity 0.4s ease';
      botMsg.style.opacity = 1;
    }, 50);

    chatbox.scrollTop = chatbox.scrollHeight;

  } catch (err) {
    // Remove loading message on error
    const loadingElem = document.getElementById('loading');
    if (loadingElem) chatbox.removeChild(loadingElem);

    chatbox.innerHTML += `<div class="msg bot">⚠️ Error: ${err.message}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight;
  }
}

// Handle Enter key and optional button click
document.addEventListener('DOMContentLoaded', () => {
  const inputField = document.getElementById('input');
  inputField.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      send();
    }
  });

  // Optional send button support (if you add a button with id="sendBtn")
  const sendBtn = document.getElementById('sendBtn');
  if (sendBtn) {
    sendBtn.addEventListener('click', send);
  }
});
