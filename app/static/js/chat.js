const messages = [];
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const welcome = document.getElementById('welcome');

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !sendBtn.disabled) sendMessage();
});

function useSuggestion(el) {
    userInput.value = el.textContent;
    sendMessage();
}

function addMessage(role, text) {
    if (welcome) welcome.style.display = 'none';

    const group = document.createElement('div');
    group.className = `message-group ${role}`;

    const div = document.createElement('div');
    div.className = `message ${role}`;
    if (role === 'assistant') {
        // Render markdown and sanitize to prevent XSS from LLM output
        div.innerHTML = DOMPurify.sanitize(marked.parse(text));
    } else {
        div.textContent = text;
    }
    group.appendChild(div);

    if (role === 'assistant') {
        const feedback = document.createElement('div');
        feedback.className = 'message-feedback';
        feedback.innerHTML = `
            <button class="feedback-btn" onclick="toggleFeedback(this)" aria-label="Helpful">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/>
                    <path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                </svg>
            </button>
            <button class="feedback-btn" onclick="toggleFeedback(this)" aria-label="Not helpful">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"/>
                    <path d="M17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"/>
                </svg>
            </button>
        `;
        group.appendChild(feedback);
    }

    chatArea.appendChild(group);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function toggleFeedback(btn) {
    const siblings = btn.parentElement.querySelectorAll('.feedback-btn');
    const wasActive = btn.classList.contains('active');
    siblings.forEach(b => b.classList.remove('active'));
    if (!wasActive) btn.classList.add('active');
}

async function sendMessage() {
    const apiKey = document.getElementById('apiKey').value.trim();
    const text = userInput.value.trim();
    if (!apiKey) { addMessage('error', 'Please enter your Anthropic API key.'); return; }
    if (!text) return;

    addMessage('user', text);
    messages.push({ role: 'user', content: text });
    userInput.value = '';
    sendBtn.disabled = true;

    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div> Thinking\u2026';
    chatArea.appendChild(loading);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, messages: messages.map(m => ({ role: m.role, content: m.content })) }),
        });
        loading.remove();
        if (!res.ok) {
            const err = await res.json();
            const detail = err.detail;
            const msg = Array.isArray(detail) ? detail.map(d => d.msg).join('; ') : detail || 'Something went wrong.';
            addMessage('error', msg);
            return;
        }
        const data = await res.json();
        addMessage('assistant', data.response);
        messages.push({ role: 'assistant', content: data.response });
    } catch (e) {
        loading.remove();
        addMessage('error', 'Network error. Is the server running?');
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}


