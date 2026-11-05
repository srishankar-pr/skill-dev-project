/**
 * Technical Rule-Based Chatbot Module (chatbot.html)
 * Connects to POST /chat via Fetch API and renders structured technical explanations,
 * code snippets, matched rule topics, and follow-up suggestion chips.
 */

function formatMarkdownLite(text) {
  let safe = escapeHtml(text);
  // Headings
  safe = safe.replace(/^### (.+)$/gm, '<strong style="font-size:1rem; display:block; margin-bottom:6px; color:var(--primary);">$1</strong>');
  // Bold
  safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Inline code
  safe = safe.replace(/`([^`]+)`/g, '<code style="background:var(--bg-subtle); padding:2px 6px; border-radius:4px; font-size:0.82rem;">$1</code>');
  // Line breaks
  safe = safe.replace(/\n/g, '<br>');
  return safe;
}

function appendUserBubble(message) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble user';
  bubble.innerHTML = `<div>${escapeHtml(message)}</div>`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function appendBotBubble(response) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble bot';

  const keywordsText =
    response.matched_keywords && response.matched_keywords.length > 0
      ? `Keywords: ${response.matched_keywords.join(', ')}`
      : 'Rule Fallback';

  const codeHtml = response.code_example
    ? `<pre class="chat-code-block"><code>${escapeHtml(response.code_example)}</code></pre>`
    : '';

  const chipsHtml =
    response.follow_up_suggestions && response.follow_up_suggestions.length > 0
      ? `<div class="chip-list">
          ${response.follow_up_suggestions
            .map(
              (s) =>
                `<button type="button" class="topic-chip" onclick="sendPresetQuery('${escapeHtml(s).replace(/'/g, "\\'")}')">${escapeHtml(s)}</button>`
            )
            .join('')}
        </div>`
      : '';

  bubble.innerHTML = `
    <div class="chat-meta-header">
      <span class="badge badge-category">Topic: ${escapeHtml(response.matched_topic)}</span>
      <span>${escapeHtml(response.confidence)} (${escapeHtml(keywordsText)})</span>
    </div>
    <div>${formatMarkdownLite(response.reply)}</div>
    ${codeHtml}
    ${chipsHtml}
  `;

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage(messageText) {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send-btn');
  const query = (messageText !== undefined ? messageText : input?.value || '').trim();

  if (!query) return;
  if (input && messageText === undefined) input.value = '';

  appendUserBubble(query);
  if (sendBtn) sendBtn.disabled = true;

  try {
    const response = await apiFetch('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: query,
        student_id: STUDENT_ID,
      }),
    });
    appendBotBubble(response);
  } catch (err) {
    appendBotBubble({
      reply: `Error communicating with /chat endpoint: ${err.message}`,
      matched_topic: 'System Error',
      confidence: 'N/A',
      matched_keywords: [],
      follow_up_suggestions: ['Hello', 'Help'],
      code_example: null,
    });
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    if (input) input.focus();
  }
}

function sendPresetQuery(queryText) {
  sendChatMessage(queryText);
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      sendChatMessage();
    });
  }

  // Load initial greeting from the rule-based assistant
  if (document.getElementById('chat-messages')) {
    sendChatMessage('hello');
  }
});
