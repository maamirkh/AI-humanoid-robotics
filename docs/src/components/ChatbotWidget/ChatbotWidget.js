import React, { useState, useEffect } from 'react';
import styles from './ChatbotWidget.module.css';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Initialize with a welcome message and create session
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 1,
          text: "Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook. Ask me anything about the content!",
          isBot: true,
          timestamp: new Date()
        }
      ]);

      // Create a new session when the component mounts
      createNewSession();
    }
  }, [messages.length]);

  const createNewSession = async () => {
    try {
      const backendUrl = typeof window !== 'undefined' && window.CHATBOT_BACKEND_URL
        ? window.CHATBOT_BACKEND_URL
        : process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

      const response = await fetch(`${backendUrl}/api/v1/chat/session/new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
      } else {
        console.error('Failed to create session');
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const backendUrl = typeof window !== 'undefined' && window.CHATBOT_BACKEND_URL
        ? window.CHATBOT_BACKEND_URL
        : process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

      // Call the backend API
      const response = await fetch(`${backendUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          session_id: sessionId
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id); // Update session ID if it changed

        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          isBot: true,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorData = await response.json();
        const errorMessage = {
          id: Date.now() + 1,
          text: `Sorry, I encountered an error: ${errorData.detail || 'Please try again.'}`,
          isBot: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm unable to connect to the server. Please check that the backend is running.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection.toString().trim()) {
      setInputValue(`About this text: "${selection.toString().trim()}": ${inputValue}`);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* Floating button to open/close chat */}
      <button
        className={`${styles.chatButton} ${isOpen ? styles.hidden : ''}`}
        onClick={toggleChat}
        aria-label="Open chatbot"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12C2 13.54 2.36 15.01 3.02 16.32L2 22L7.68 20.98C8.99 21.64 10.46 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="white"/>
          <path d="M9.5 14.5L14.5 9.5M14.5 9.5H9.5M14.5 9.5V14.5" stroke="#111827" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Chat window */}
      <div className={`${styles.chatWindow} ${isOpen ? styles.open : ''}`}>
        <div className={styles.chatHeader}>
          <h3>Textbook Assistant</h3>
          <button
            className={styles.closeButton}
            onClick={toggleChat}
            aria-label="Close chat"
          >
            ×
          </button>
        </div>

        <div className={styles.chatMessages}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${message.isBot ? styles.botMessage : styles.userMessage}`}
            >
              <div className={styles.messageContent}>
                {message.text}
              </div>
              <div className={styles.messageTimestamp}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className={styles.message + ' ' + styles.botMessage}>
              <div className={styles.typingIndicator}>
                <div className={styles.typingDot}></div>
                <div className={styles.typingDot}></div>
                <div className={styles.typingDot}></div>
              </div>
            </div>
          )}
        </div>

        <form className={styles.chatInputForm} onSubmit={handleSendMessage}>
          <div className={styles.inputActions}>
            <button
              type="button"
              className={styles.textSelectionButton}
              onClick={handleTextSelection}
              title="Ask about selected text"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3H13V4H3V3ZM3 6H13V7H3V6ZM3 9H10V10H3V9ZM3 12H7V13H3V12Z" fill="currentColor"/>
              </svg>
            </button>
          </div>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about the textbook content..."
            className={styles.chatInput}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={isLoading || !inputValue.trim()}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 1L9 7L15 13L14 8L1 15L8 8L1 1L15 1Z" fill="currentColor"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatbotWidget;