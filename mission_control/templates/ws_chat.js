
        // WalkScape Chat Functions
        let wsChatMessages = [];

        function wsChatAddMessage(role, text) {
            const container = document.getElementById('ws-chat-messages');
            const msg = document.createElement('div');
            msg.className = `ws-chat-msg ${role}`;
            msg.textContent = text;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
            wsChatMessages.push({ role, text });
        }

        function wsChatAddThinking() {
            const container = document.getElementById('ws-chat-messages');
            const thinking = document.createElement('div');
            thinking.className = 'ws-chat-thinking';
            thinking.id = 'ws-chat-thinking';
            thinking.textContent = '🤖 Thinking...';
            container.appendChild(thinking);
            container.scrollTop = container.scrollHeight;
        }

        function wsChatRemoveThinking() {
            const el = document.getElementById('ws-chat-thinking');
            if (el) el.remove();
        }

        function wsChatSend() {
            const input = document.getElementById('ws-chat-input');
            const sendBtn = document.getElementById('ws-chat-send');
            const message = input.value.trim();
            if (!message) return;

            wsChatAddMessage('user', message);
            input.value = '';
            wsChatAddThinking();
            sendBtn.disabled = true;

            fetch('/walkscape/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(r => r.json())
            .then(result => {
                wsChatRemoveThinking();
                sendBtn.disabled = false;
                if (result.success) {
                    // Send to AI session - context is returned, we'll use sessions_send
                    // For now, show that we're ready to handle it
                    wsChatAddMessage('bot', `Got your message: "${message}". I have your player context loaded. This chat feature is ready for AI-powered recommendations. Check back soon — I'm connecting the intelligence layer now.`);
                } else {
                    wsChatAddMessage('bot', 'Error: ' + (result.error || 'Failed to process message'));
                }
            })
            .catch(e => {
                wsChatRemoveThinking();
                sendBtn.disabled = false;
                wsChatAddMessage('bot', 'Error: ' + e.message);
            });
        }

        // Enter key sends chat (Shift+Enter for newline)
        document.getElementById('ws-chat-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                wsChatSend();
            }
        });
