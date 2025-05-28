import React, { useState, useEffect, useRef } from 'react';
import { Send, Person, SmartToy } from '@mui/icons-material';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    position: "relative"
  },
  header: {
    background: "linear-gradient(135deg, #1F1B24 0%, #2A3B4D 100%)",
    padding: "1rem 2rem",
    borderBottom: "1px solid rgba(255, 99, 71, 0.2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
  },
  headerTitle: {
    color: "#E0E0E0",
    fontSize: "1.5rem",
    fontWeight: "700",
    margin: 0
  },
  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    maxHeight: "calc(100vh - 80px)",
    padding: "0"
  },
  messagesArea: {
    flex: 1,
    overflowY: "auto",
    padding: "2rem",
    background: "#121212"
  },
  welcomeMessage: {
    textAlign: "center",
    color: "#7A8FA6",
    fontSize: "1.2rem",
    padding: "4rem 2rem",
    background: "rgba(31, 27, 36, 0.3)",
    borderRadius: "16px",
    margin: "2rem auto",
    maxWidth: "600px",
    border: "1px solid rgba(255, 99, 71, 0.1)"
  },
  message: {
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    marginBottom: "1.5rem",
    padding: "16px",
    borderRadius: "16px",
    maxWidth: "85%",
    animation: "fadeIn 0.3s ease"
  },
  userMessage: {
    backgroundColor: "rgba(255, 99, 71, 0.1)",
    border: "1px solid rgba(255, 99, 71, 0.2)",
    marginLeft: "auto",
    flexDirection: "row-reverse"
  },
  aiMessage: {
    backgroundColor: "rgba(31, 27, 36, 0.8)",
    border: "1px solid #2A3B4D"
  },
  loadingMessage: {
    backgroundColor: "rgba(31, 27, 36, 0.8)",
    border: "1px solid #2A3B4D",
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    marginBottom: "1.5rem",
    padding: "16px",
    borderRadius: "16px",
    maxWidth: "85%",
    animation: "pulse 1.5s ease-in-out infinite"
  },
  loadingDots: {
    display: "inline-block",
    color: "#7A8FA6",
    animation: "loadingDots 1.5s infinite"
  },
  inputArea: {
    background: "linear-gradient(135deg, #1F1B24 0%, #2A3B4D 100%)",
    padding: "1.5rem 2rem",
    borderTop: "1px solid rgba(255, 99, 71, 0.2)",
    display: "flex",
    gap: "16px",
    alignItems: "center",
    boxShadow: "0 -2px 8px rgba(0,0,0,0.3)"
  },
  input: {
    flex: 1,
    padding: "16px 20px",
    borderRadius: "30px",
    border: "1px solid #2A3B4D",
    backgroundColor: "#121212",
    color: "#E0E0E0",
    fontSize: "1rem",
    outline: "none",
    transition: "all 0.3s ease",
    resize: "none",
    minHeight: "20px",
    maxHeight: "120px"
  },
  sendButton: {
    padding: "16px 24px",
    borderRadius: "30px",
    border: "none",
    background: "linear-gradient(135deg, #FF6347 0%, #FF4500 100%)",
    color: "#fff",
    cursor: "pointer",
    fontWeight: "700",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    transition: "all 0.3s ease",
    fontSize: "1rem",
    boxShadow: "0 4px 12px rgba(255, 99, 71, 0.3)"
  },
  errorMessage: {
    padding: "12px 20px",
    backgroundColor: "rgba(255, 99, 71, 0.1)",
    border: "1px solid rgba(255, 99, 71, 0.3)",
    borderRadius: "12px",
    color: "#FF6347",
    margin: "1rem 2rem",
    textAlign: "center"
  },
  "@keyframes loadingDots": {
    "0%": { content: "." },
    "33%": { content: ".." },
    "66%": { content: "..." },
    "100%": { content: "." }
  },
  "@keyframes pulse": {
    "0%": { opacity: 0.6 },
    "50%": { opacity: 0.8 },
    "100%": { opacity: 0.6 }
  }
};

function UserChat() {
  const params = new URLSearchParams(window.location.search);
  const uuid = params.get('user');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);  // Changed to true initially
  const chatEndRef = useRef(null);

  // Add this new useEffect to fetch initial chat history
  useEffect(() => {
    const fetchInitialHistory = async () => {
      try {
        const res = await fetch(`/api/user_chat/${uuid}`);
        const data = await res.json();
        if (data.error) {
          setError(data.error);
        } else if (data.history) {
          setMessages(data.history);
        }
      } catch (e) {
        setError('Failed to load chat history');
      } finally {
        setIsLoading(false);
      }
    };

    if (uuid) {
      fetchInitialHistory();
    }
  }, [uuid]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const [isChatEnded, setIsChatEnded] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isChatEnded) return;
    setMessages([...messages, { role: 'user', message: input }]);
    const currentInput = input;
    setInput('');
    setError('');
    setIsLoading(true);
    
    try {
      const res = await fetch(`/api/user_chat/${uuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setMessages(msgs => [...msgs, { role: 'ai', message: data.response }]);
        // Check if the AI response contains the ending phrase
        if (data.response.toLowerCase().includes('have a great day')) {
          setIsChatEnded(true);
        }
      }
    } catch (e) {
      setError('Network error - please try again');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.headerTitle}>Chat with Caze Representative</h1>
      </div>
      
      <div style={styles.chatContainer}>
        <div style={styles.messagesArea}>
          {messages.length === 0 && (
            <div style={styles.welcomeMessage}>
              Welcome! How can I assist you today?
            </div>
          )}
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.message,
                ...(msg.role === 'user' ? styles.userMessage : styles.aiMessage)
              }}
            >
              {msg.role === 'user' ? (
                <Person sx={{ color: '#FF6347' }} />
              ) : (
                <SmartToy sx={{ color: '#7A8FA6' }} />
              )}
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.message}</div>
            </div>
          ))}
          {isLoading && (
            <div style={styles.loadingMessage}>
              <SmartToy sx={{ color: '#7A8FA6' }} />
              <div style={{ whiteSpace: 'pre-wrap' }}>
                Generating response
                <span style={styles.loadingDots}>...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {error && <div style={styles.errorMessage}>{error}</div>}

        {isChatEnded && (
          <div style={{
            ...styles.errorMessage,
            backgroundColor: 'rgba(122, 143, 166, 0.1)',
            border: '1px solid rgba(122, 143, 166, 0.3)',
            color: '#7A8FA6'
          }}>
            This conversation has ended. Thank you for chatting with us!
          </div>
        )}
        <div style={styles.inputArea}>
          <textarea
            style={{
              ...styles.input,
              opacity: isChatEnded ? 0.5 : 1,
              cursor: isChatEnded ? 'not-allowed' : 'text'
            }}
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={isChatEnded ? "Chat has ended" : "Type your message..."}
            rows={1}
            disabled={isChatEnded}
          />
          <button
            style={{
              ...styles.sendButton,
              opacity: isChatEnded ? 0.5 : 1,
              cursor: isChatEnded ? 'not-allowed' : 'pointer'
            }}
            onClick={sendMessage}
            disabled={!input.trim() || isChatEnded}
          >
            <Send />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default UserChat;