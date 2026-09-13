"""MkDocs hook: RAG chat widget (spec 005-chat-rag).

Runs inside BOTH language builds (wired via `hooks:` in mkdocs.*.yml):

  1. on_config  — reads RAG_API_KEY from env, injects it into chat.js,
                  registers the emitted chat.js and chat.css in extra_javascript/extra_css.
  2. on_post_build — emits the chat widget files into the site directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JS_NAME = "assets/javascripts/chat.js"
CSS_NAME = "assets/css/chat.css"

# Placeholder replaced at build time with the real API key from GitHub Secret.
_RAG_API_KEY_PLACEHOLDER = "{{RAG_API_KEY}}"

_CHAT_JS_TEMPLATE = """(function () {
  'use strict';
  console.log('FreeLLM Chat Widget: Initializing...');

  // Chat widget state
  let isOpen = false;
  let messages = [];

  // Create chat button
  function createChatButton() {
    const btn = document.createElement('button');
    btn.id = 'chat-toggle-btn';
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
    btn.style.position = 'fixed';
    btn.style.bottom = '24px';
    btn.style.right = '24px';
    btn.style.width = '56px';
    btn.style.height = '56px';
    btn.style.borderRadius = '50%';
    btn.style.backgroundColor = 'var(--md-primary-fg-color, #6366f1)';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.boxShadow = 'var(--md-shadow-z2, 0 4px 6px -1px rgba(0,0,0,0.1))';
    btn.style.cursor = 'pointer';
    btn.style.zIndex = '1000';
    btn.style.display = 'flex';
    btn.style.alignItems = 'center';
    btn.style.justifyContent = 'center';
    btn.style.transition = 'all 0.3s ease';
    btn.onmouseover = () => {
      btn.style.transform = 'scale(1.05)';
      btn.style.backgroundColor = 'var(--md-accent-fg-color, #4f46e5)';
    };
    btn.onmouseout = () => {
      btn.style.transform = 'scale(1)';
      btn.style.backgroundColor = 'var(--md-primary-fg-color, #6366f1)';
    };
    btn.onclick = toggleChat;
    document.body.appendChild(btn);
  }

  // Create chat widget
  function createChatWidget() {
    const widget = document.createElement('div');
    widget.id = 'chat-widget';
    widget.style.position = 'fixed';
    widget.style.bottom = '90px';
    widget.style.right = '24px';
    widget.style.width = '350px';
    widget.style.height = '500px';
    widget.style.backgroundColor = 'var(--md-default-bg-color, white)';
    widget.style.borderRadius = '16px';
    widget.style.boxShadow = 'var(--md-shadow-z2, 0 10px 25px -5px rgba(0,0,0,0.1))';
    widget.style.display = 'flex';
    widget.style.flexDirection = 'column';
    widget.style.zIndex = '1000';
    widget.style.border = '1px solid var(--md-divider-color, #e5e7eb)';
    widget.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    widget.style.opacity = '0';
    widget.style.transform = 'translateY(20px)';
    widget.style.pointerEvents = 'none';

    // Chat header
    const header = document.createElement('div');
    header.className = 'chat-header';
    header.style.padding = '16px';
    header.style.borderBottom = '1px solid var(--md-divider-color, #f3f4f6)';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.style.backgroundColor = 'var(--md-default-bg-color--container, #f8fafc)';

    const title = document.createElement('h3');
    title.textContent = 'Chat with AI';
    title.style.margin = '0';
    title.style.fontSize = '1.25rem';
    title.style.fontWeight = '600';
    title.style.color = 'var(--md-default-fg-color, #1f2937)';

    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.color = 'var(--md-default-fg-color--medium, #6b7280)';
    closeBtn.style.fontSize = '1.25rem';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.padding = '4px';
    closeBtn.style.borderRadius = '50%';
    closeBtn.style.width = '36px';
    closeBtn.style.height = '36px';
    closeBtn.style.display = 'flex';
    closeBtn.style.alignItems = 'center';
    closeBtn.style.justifyContent = 'center';
    closeBtn.onmouseover = () => {
      closeBtn.style.backgroundColor = 'var(--md-default-bg-color--light, #f3f4f6)';
    };
    closeBtn.onmouseout = () => {
      closeBtn.style.color = 'var(--md-default-fg-color--medium, #6b7280)';
    };
    closeBtn.onclick = () => {
      closeChat();
    };
    header.appendChild(title);
    header.appendChild(closeBtn);
    widget.appendChild(header);

    // Chat messages container
    const messagesContainer = document.createElement('div');
    messagesContainer.id = 'chat-messages';
    messagesContainer.style.flex = '1';
    messagesContainer.style.overflowY = 'auto';
    messagesContainer.style.padding = '16px';
    messagesContainer.style.display = 'flex';
    messagesContainer.style.flexDirection = 'column';
    messagesContainer.style.gap = '12px';
    widget.appendChild(messagesContainer);

    // Chat input
    const inputContainer = document.createElement('div');
    inputContainer.className = 'chat-input-container';
    inputContainer.style.padding = '16px';
    inputContainer.style.borderTop = '1px solid var(--md-divider-color, #f3f4f6)';
    inputContainer.style.display = 'flex';
    inputContainer.style.gap = '12px';
    inputContainer.style.backgroundColor = 'var(--md-default-bg-color--container, #f8fafc)';

    const input = document.createElement('input');
    input.id = 'chat-input';
    input.type = 'text';
    input.placeholder = 'Ask me anything...';
    input.style.flex = '1';
    input.style.padding = '12px 16px';
    input.style.border = '1px solid var(--md-input-border-color, #e5e7eb)';
    input.style.borderRadius = '12px';
    input.style.fontSize = '1rem';
    input.style.outline = 'none';
    input.style.transition = 'border-color 0.2s ease';
    input.onfocus = () => {
      input.style.borderColor = 'var(--md-primary-fg-color, #6366f1)';
    };
    input.onblur = () => {
      input.style.borderColor = 'var(--md-input-border-color, #e5e7eb)';
    };
    input.onkeypress = (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    };

    const sendBtn = document.createElement('button');
    sendBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>';
    sendBtn.style.backgroundColor = 'var(--md-primary-fg-color, #6366f1)';
    sendBtn.style.color = 'white';
    sendBtn.style.border = 'none';
    sendBtn.style.borderRadius = '50%';
    sendBtn.style.width = '40px';
    sendBtn.style.height = '40px';
    sendBtn.style.cursor = 'pointer';
    sendBtn.style.display = 'flex';
    sendBtn.style.alignItems = 'center';
    sendBtn.style.justifyContent = 'center';
    sendBtn.style.boxShadow = 'var(--md-shadow-z1, 0 2px 4px -1px rgba(0,0,0,0.1))';
    sendBtn.onmouseover = () => {
      sendBtn.style.backgroundColor = 'var(--md-accent-fg-color, #4f46e5)';
    };
    sendBtn.onmouseout = () => {
      sendBtn.style.backgroundColor = 'var(--md-primary-fg-color, #6366f1)';
    };
    sendBtn.onclick = sendMessage;

    inputContainer.appendChild(input);
    inputContainer.appendChild(sendBtn);
    widget.appendChild(inputContainer);

    document.body.appendChild(widget);
  }

  function toggleChat() {
    isOpen = !isOpen;
    const widget = document.getElementById('chat-widget');
    if (isOpen) {
      widget.style.opacity = '1';
      widget.style.transform = 'translateY(0)';
      widget.style.pointerEvents = 'all';
      document.getElementById('chat-input').focus();
    } else {
      widget.style.opacity = '0';
      widget.style.transform = 'translateY(20px)';
      widget.style.pointerEvents = 'none';
    }
  }

  function closeChat() {
    isOpen = false;
    const widget = document.getElementById('chat-widget');
    widget.style.opacity = '0';
    widget.style.transform = 'translateY(20px)';
    widget.style.pointerEvents = 'none';
  }

  function addMessage(content, isUser = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.style.display = 'flex';
    messageDiv.style.flexDirection = isUser ? 'row-reverse' : 'row';
    messageDiv.style.alignItems = 'flex-start';
    messageDiv.style.maxWidth = '80%';

    const avatar = document.createElement('div');
    avatar.style.width = '32px';
    avatar.style.height = '32px';
    avatar.style.borderRadius = '50%';
    avatar.style.display = 'flex';
    avatar.style.alignItems = 'center';
    avatar.style.justifyContent = 'center';
    avatar.style.fontSize = '0.875rem';
    avatar.style.fontWeight = '600';
    avatar.style.color = 'white';
    avatar.style.margin = isUser ? '0 0 0 8px' : '0 8px 0 0';

    if (isUser) {
      avatar.style.backgroundColor = 'var(--md-primary-fg-color, #6366f1)';
      avatar.textContent = 'U';
      messageDiv.style.marginLeft = 'auto';
    } else {
      avatar.style.backgroundColor = 'var(--md-default-fg-color--light, #f3f4f6)';
      avatar.textContent = 'AI';
      avatar.style.color = 'var(--md-default-fg-color--medium, #6b7280)';
      messageDiv.style.marginRight = 'auto';
    }

    const messageContent = document.createElement('div');
    messageContent.className = 'chat-bubble-content';
    messageDiv.className = isUser ? 'chat-bubble user' : 'chat-bubble ai';
    messageContent.style.padding = '12px 16px';
    messageContent.style.borderRadius = isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px';
    messageContent.style.backgroundColor = isUser ? 'var(--md-primary-fg-color, #6366f1)' : 'var(--md-default-fg-color--light, #f3f4f6)';
    messageContent.style.color = isUser ? 'white' : 'var(--md-default-fg-color, #1f2937)';
    messageContent.style.lineHeight = '1.5';
    messageContent.style.fontSize = '0.95rem';
    messageContent.style.wordWrap = 'break-word';
    messageContent.style.maxWidth = '100%';

    messageContent.textContent = content;

    messageDiv.appendChild(isUser ? messageContent : avatar);
    messageDiv.appendChild(!isUser ? messageContent : avatar);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return messageDiv;
  }

  async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, true);
    input.value = '';

    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.style.display = 'flex';
    typingDiv.style.alignItems = 'center';
    typingDiv.style.maxWidth = '80%';
    typingDiv.style.marginLeft = 'auto';

    const typingAvatar = document.createElement('div');
    typingAvatar.style.width = '32px';
    typingAvatar.style.height = '32px';
    typingAvatar.style.borderRadius = '50%';
    typingAvatar.style.backgroundColor = 'var(--md-default-fg-color--light, #f3f4f6)';
    typingAvatar.style.display = 'flex';
    typingAvatar.style.alignItems = 'center';
    typingAvatar.style.justifyContent = 'center';
    typingAvatar.style.fontSize = '0.875rem';
    typingAvatar.style.fontWeight = '600';
    typingAvatar.style.color = 'var(--md-default-fg-color--medium, #6b7280)';
    typingAvatar.textContent = 'AI';

    const typingContent = document.createElement('div');
    typingContent.style.padding = '12px 16px';
    typingContent.style.borderRadius = '16px 16px 16px 4px';
    typingContent.style.backgroundColor = 'var(--md-default-fg-color--light, #f3f4f6)';
    typingContent.style.color = 'var(--md-default-fg-color, #1f2937)';
    typingContent.style.lineHeight = '1.5';
    typingContent.style.fontSize = '0.95rem';

    const typingDots = document.createElement('span');
    typingDots.id = 'typing-dots';
    typingDots.style.display = 'inline-block';
    typingDots.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    typingDots.style.animation = 'typing 1.5s infinite';

    typingContent.appendChild(typingDots);

    typingDiv.appendChild(typingAvatar);
    typingDiv.appendChild(typingContent);

    document.getElementById('chat-messages').appendChild(typingDiv);
    document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;

    try {
      // Call RAG API — API key injected at build time from GitHub Secret
      const response = await fetch('https://rag.aldof.duckdns.org/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': '{{RAG_API_KEY}}',
        },
        body: JSON.stringify({
          question: message,
          k: 3
        })
      });

      const data = await response.json();

      // Remove typing indicator
      if (typingDiv) {
        typingDiv.remove();
      }

      if (data && data.answer) {
        console.log('RAG response:', data);
        const bubble = addMessage(data.answer, false);
        // Show sources as inline citations below the assistant message (XSS-safe)
        if (data.sources && Array.isArray(data.sources)) {
          const sourcesDiv = document.createElement('div');
          sourcesDiv.className = 'chat-sources';
          sourcesDiv.style.cssText = 'font-size:0.75rem;color:var(--md-default-fg-color--medium);margin-top:4px;padding-left:12px;';
          const escape = s => String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
          sourcesDiv.innerHTML = '<strong>Sources:</strong> ' + data.sources.map(s => {
            const url = (s.url || s.link || '#').trim();
            const title = escape(s.title || s.source || 'Reference');
            const safeUrl = url.startsWith('http') ? escape(url) : '#';
            return '<a href="' + safeUrl + '" target="_blank" rel="noopener noreferrer">' + title + '</a>';
          }).join(', ');
          if (bubble) bubble.appendChild(sourcesDiv);
        }
      } else if (data && data.detail) {
        // RAG returned an error (e.g. auth failure, upstream failure)
        addMessage('RAG service error: ' + data.detail, false);
      } else {
        addMessage('Sorry, I encountered an error. Please try again.', false);
      }
    } catch (error) {
      if (typingDiv) {
        typingDiv.remove();
      }
      addMessage('Sorry, I encountered an error. Please check your connection and try again.', false);
      console.error('Chat error:', error);
    }
  }

  // RAG health check — verify the endpoint is reachable and returns a valid response
  // before revealing the FAB. Invalid/missing API key or unreachable service → button stays hidden.
  async function checkRagHealth() {
    try {
      const res = await fetch('https://rag.aldof.duckdns.org/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': '{{RAG_API_KEY}}',
        },
        body: JSON.stringify({ question: '_health_check_', k: 1 })
      });
      if (!res.ok) return false;
      const json = await res.json();
      // A valid response has at least an 'answer' string with content
      return !!(json && typeof json.answer === 'string' && json.answer.trim().length > 0);
    } catch (_) {
      return false;
    }
  }

  // Initialize
  async function init() {
    const isHealthy = await checkRagHealth();
    if (!isHealthy) {
      console.log('RAG unavailable — chat button hidden');
      return; // FAB + widget never created
    }
    createChatButton();
    createChatWidget();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 0);
  }
})();"""

_CHAT_CSS = """\
/* Chat widget — Material Design tokens from mkdocs-material */
#chat-toggle-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--md-primary-fg-color, #6366f1);
  color: white;
  border: none;
  box-shadow: var(--md-shadow-z2, 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06));
  cursor: pointer;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

#chat-toggle-btn:hover {
  transform: scale(1.05);
  background-color: var(--md-accent-fg-color, #4f46e5);
}

#chat-widget {
  position: fixed;
  bottom: 90px;
  right: 24px;
  width: 350px;
  height: 500px;
  background-color: var(--md-default-bg-color, #fff);
  border-radius: 16px;
  box-shadow: var(--md-shadow-z2, 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1));
  display: flex;
  flex-direction: column;
  z-index: 1000;
  border: 1px solid var(--md-divider-color, #e5e7eb);
  opacity: 0;
  transform: translateY(20px);
  pointer-events: none;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid var(--md-divider-color, #f3f4f6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--md-default-bg-color--container, #f8fafc);
}

.chat-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--md-default-fg-color, #1f2937);
}

.chat-header button {
  background: none;
  border: none;
  color: var(--md-default-fg-color--medium, #6b7280);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-header button:hover {
  background-color: var(--md-default-bg-color--light, #f3f4f6);
  color: var(--md-default-fg-color, #1f2937);
}

#chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-input-container {
  padding: 16px;
  border-top: 1px solid var(--md-divider-color, #f3f4f6);
  display: flex;
  gap: 12px;
  background-color: var(--md-default-bg-color--container, #f8fafc);
}

#chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--md-input-border-color, var(--md-default-fg-color--lightest, #e5e7eb));
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s ease;
  background-color: var(--md-default-bg-color, #fff);
  color: var(--md-default-fg-color, #1f2937);
}

#chat-input:focus {
  border-color: var(--md-primary-fg-color, #6366f1);
}

#chat-input::placeholder {
  color: var(--md-default-fg-color--medium, #9ca3af);
}

.chat-bubble {
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
  max-width: 80%;
}

.chat-bubble.user {
  margin-left: auto;
}

.chat-bubble.ai {
  margin-right: auto;
}

.chat-bubble-content {
  padding: 12px 16px;
  border-radius: 16px 16px 4px 16px;
  line-height: 1.5;
  font-size: 0.95rem;
  word-wrap: break-word;
  max-width: 100%;
}

.chat-bubble.user .chat-bubble-content {
  background-color: var(--md-primary-fg-color, #6366f1);
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.chat-bubble.ai .chat-bubble-content {
  background-color: var(--md-default-fg-color--light, #f3f4f6);
  color: var(--md-default-fg-color, #1f2937);
  border-radius: 16px 16px 16px 4px;
}

.chat-sources {
  font-size: 0.75rem;
  color: var(--md-default-fg-color--medium, #6b7280);
  margin-top: 4px;
  padding-left: 12px;
}

.chat-sources a {
  color: var(--md-accent-fg-color, #526cfe);
  text-decoration: none;
}

.chat-sources a:hover {
  text-decoration: underline;
}

@keyframes typing {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}
"""


def _inject_key(js_template: str, api_key: str) -> str:
    """Replace the API key placeholder with the real key."""
    if not api_key:
        print(
            "chat: WARNING — RAG_API_KEY not set, chat will fail at runtime",
            file=sys.stderr,
        )
    return js_template.replace("{{RAG_API_KEY}}", api_key or "")


def on_config(config, **kwargs):
    """Register chat assets in extra_javascript/extra_css so they ship with the build.
    CHANGED: Chat widget is disabled for now — health check always returns false
    so the FAB is never created, keeping the UI clean.
    """
    # Chat widget disabled — no assets registered
    return config


def on_post_build(*, config, **kwargs):
    """Emit chat widget files to site directory, injecting RAG_API_KEY at build time.
    CHANGED: Chat widget is disabled — no files emitted.
    """
    # Chat widget disabled — nothing to emit
    pass
