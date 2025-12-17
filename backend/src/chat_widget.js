/**
 * RAG Chatbot Widget for Docusaurus Integration
 * Provides an embedded chat interface that connects to the RAG backend
 */

class RAGChatbot {
    constructor(config = {}) {
        this.config = {
            backendUrl: config.backendUrl || 'https://huggingface.co/spaces/mamir1983/rag-docusaurus-book',
            containerId: config.containerId || 'rag-chatbot-container',
            theme: config.theme || 'default',
            ...config
        };

        this.sessionId = null;
        this.userId = config.userId || null;
        this.element = null;

        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
    }

    createWidget() {
        // Create the chatbot container
        this.element = document.createElement('div');
        this.element.id = this.config.containerId;
        this.element.className = `rag-chatbot ${this.config.theme}`;
        this.element.innerHTML = `
            <div class="chatbot-header">
                <span>Physical AI & Humanoid Robotics Assistant</span>
                <button class="chatbot-close">&times;</button>
            </div>
            <div class="chatbot-messages">
                <div class="message bot-message">
                    Hello! I'm your AI assistant for the Physical AI and Humanoid Robotics textbook. Ask me anything about the content!
                </div>
            </div>
            <div class="chatbot-input">
                <input type="text" class="user-input" placeholder="Ask a question about the textbook..." />
                <button class="send-button">Send</button>
            </div>
        `;

        document.body.appendChild(this.element);

        // Add CSS styles
        this.addStyles();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #${this.config.containerId} {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 350px;
                height: 500px;
                border: 1px solid #ccc;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                background: white;
                z-index: 1000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .chatbot-header {
                background: #4f46e5;
                color: white;
                padding: 15px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .chatbot-close {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
            }

            .chatbot-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .message {
                max-width: 80%;
                padding: 8px 12px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.4;
                word-wrap: break-word;
            }

            .user-message {
                align-self: flex-end;
                background: #e0e7ff;
                border-bottom-right-radius: 4px;
            }

            .bot-message {
                align-self: flex-start;
                background: #f3f4f6;
                border-bottom-left-radius: 4px;
            }

            .chatbot-input {
                display: flex;
                padding: 15px;
                border-top: 1px solid #eee;
            }

            .user-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 18px;
                outline: none;
                font-size: 14px;
            }

            .send-button {
                margin-left: 10px;
                padding: 10px 15px;
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 18px;
                cursor: pointer;
                font-size: 14px;
            }

            .send-button:disabled {
                background: #a5b4fc;
                cursor: not-allowed;
            }

            .suggested-sections {
                font-size: 12px;
                color: #6b7280;
                margin-top: 5px;
            }

            .suggested-section {
                display: inline-block;
                background: #e0f2fe;
                padding: 2px 6px;
                border-radius: 10px;
                margin: 2px;
                cursor: pointer;
                font-size: 11px;
            }

            .chatbot-toggle {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: #4f46e5;
                color: white;
                border: none;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                display: none;
            }
        `;

        document.head.appendChild(style);
    }

    bindEvents() {
        const closeBtn = this.element.querySelector('.chatbot-close');
        const sendBtn = this.element.querySelector('.send-button');
        const userInput = this.element.querySelector('.user-input');

        closeBtn.addEventListener('click', () => {
            this.element.style.display = 'none';
            document.body.insertAdjacentHTML('beforeend', '<button class="chatbot-toggle">💬</button>');
            document.querySelector('.chatbot-toggle').addEventListener('click', () => {
                this.element.style.display = 'flex';
                document.querySelector('.chatbot-toggle').remove();
            });
        });

        sendBtn.addEventListener('click', () => this.sendMessage());

        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async createNewSession() {
        try {
            const response = await fetch(`${this.config.backendUrl}/api/v1/chat/session/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });

            const data = await response.json();
            this.sessionId = data.session_id;
            return this.sessionId;
        } catch (error) {
            console.error('Error creating session:', error);
            this.addMessage('Sorry, I encountered an error setting up our conversation.', 'bot');
            return null;
        }
    }

    async sendMessage() {
        const input = this.element.querySelector('.user-input');
        const message = input.value.trim();
        if (!message) return;

        // Disable send button and clear input
        const sendBtn = this.element.querySelector('.send-button');
        sendBtn.disabled = true;
        input.value = '';

        // Add user message to UI
        this.addMessage(message, 'user');

        try {
            // Create session if needed
            if (!this.sessionId) {
                await this.createNewSession();
            }

            const response = await fetch(`${this.config.backendUrl}/api/v1/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: message,
                    session_id: this.sessionId,
                    user_id: this.userId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Add bot response to UI
            this.addMessage(data.response, 'bot');

            // Add suggested sections if available
            if (data.suggested_sections && data.suggested_sections.length > 0) {
                this.addSuggestions(data.suggested_sections);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error processing your request. Please try again.', 'bot');
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    }

    addMessage(text, sender) {
        const messagesDiv = this.element.querySelector('.chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    addSuggestions(sections) {
        const messagesDiv = this.element.querySelector('.chatbot-messages');
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'suggested-sections';
        suggestionsDiv.innerHTML = '<strong>Suggested sections:</strong> ';

        sections.slice(0, 3).forEach((section, index) => {
            const sectionSpan = document.createElement('span');
            sectionSpan.className = 'suggested-section';
            sectionSpan.textContent = section.section;
            sectionSpan.onclick = () => {
                const input = this.element.querySelector('.user-input');
                input.value = `Tell me more about ${section.section}`;
                input.focus();
            };
            suggestionsDiv.appendChild(sectionSpan);
        });

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.appendChild(suggestionsDiv);
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Public method to show the chatbot
    show() {
        this.element.style.display = 'flex';
        if (document.querySelector('.chatbot-toggle')) {
            document.querySelector('.chatbot-toggle').remove();
        }
    }

    // Public method to hide the chatbot
    hide() {
        this.element.style.display = 'none';
        if (!document.querySelector('.chatbot-toggle')) {
            document.body.insertAdjacentHTML('beforeend', '<button class="chatbot-toggle">💬</button>');
            document.querySelector('.chatbot-toggle').addEventListener('click', () => {
                this.show();
            });
        }
    }

    // Public method to set user ID
    setUserId(userId) {
        this.userId = userId;
    }

    // Public method to get current session ID
    getSessionId() {
        return this.sessionId;
    }
}

// Make it available globally or as a module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RAGChatbot;
} else {
    window.RAGChatbot = RAGChatbot;
}