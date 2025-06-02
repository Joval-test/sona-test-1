import React, { useState, useEffect, useRef } from 'react';
import { Send, Person, SmartToy } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  header: {
    width: "100vw",
    background: "linear-gradient(135deg, #1F1B24 0%, #2A3B4D 100%)",
    padding: "1.2rem 2rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
    position: "fixed", // changed from "sticky"
    top: 0,
    left: 0,
    zIndex: 100,
  },
  headerTitle: {
    color: "#E0E0E0",
    fontSize: "1.5rem",
    fontWeight: "700",
    margin: 0
  },
  chatArea: {
    flex: 1,
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-end",
    paddingBottom: "110px",
    paddingTop: "96px", // adjust to header height
    overflow: "auto"
  },
  messagesArea: {
    width: "100%",
    maxWidth: "820px", // wider like Claude
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
    padding: "0 24px",
  },
  message: {
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    padding: "18px 24px",
    borderRadius: "16px",
    maxWidth: "75%", // limit width for each message bubble
    wordBreak: "break-word",
    background: "rgba(36, 40, 47, 0.85)",
    fontSize: "1.1rem",
    lineHeight: 1.7,
    marginBottom: "1.5rem",
  },
  userMessage: {
    backgroundColor: "#3a8dde",
    color: "#fff",
    alignSelf: "flex-end",
    flexDirection: "row-reverse",
    marginLeft: "auto",   // push to right
    marginRight: "0",
    textAlign: "right",
  },
  aiMessage: {
    backgroundColor: "#23272f",
    color: "#E0E0E0",
    alignSelf: "flex-start",
    flexDirection: "row",
    marginRight: "auto",  // push to left
    marginLeft: "0",
    textAlign: "left",
  },
  loadingMessage: {
    backgroundColor: "#23272f",
    border: "none",
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    padding: "18px 24px",
    borderRadius: "16px",
    maxWidth: "100%",
    animation: "pulse 1.5s ease-in-out infinite",
    margin: "0 auto",
  },
  loadingDots: {
    display: "inline-block",
    color: "#7A8FA6",
    animation: "loadingDots 1.5s infinite"
  },
  inputBarWrapper: {
    width: "100vw",
    display: "flex",
    justifyContent: "center",
    position: "fixed",
    bottom: 0,
    left: 0,
    background: "rgba(18,18,18,0.95)",
    padding: "24px 0 16px 0",
    zIndex: 20,
    borderTop: "1px solid #23272f"
  },
  inputArea: {
    width: "100%",
    maxWidth: "820px",
    display: "flex",
    gap: "14px",
    alignItems: "center",
    background: "#23272f",
    borderRadius: "24px",
    padding: "10px 18px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.03)"
  },
  input: {
    flex: 1,
    padding: "14px 18px",
    borderRadius: "18px",
    border: "none",
    backgroundColor: "#181818",
    color: "#E0E0E0",
    fontSize: "1.1rem",
    outline: "none",
    transition: "all 0.3s ease",
    resize: "none",
    minHeight: "24px",
    maxHeight: "120px"
  },
  sendButton: {
    padding: "12px 24px",
    borderRadius: "18px",
    border: "none",
    background: "linear-gradient(135deg, #4ba7f3 0%, #2196F3 100%)",
    color: "#fff",
    cursor: "pointer",
    fontWeight: "700",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    transition: "all 0.3s ease",
    fontSize: "1.1rem",
    boxShadow: "0 4px 12px rgba(255, 99, 71, 0.08)"
  },
  errorMessage: {
    padding: "12px 20px",
    backgroundColor: "rgb(255, 99, 71)",
    border: "none",
    borderRadius: "12px",
    color: "#FF6347",
    margin: "1rem auto",
    textAlign: "center",
    maxWidth: "600px"
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
  const [isLoading, setIsLoading] = useState(true);  
  const chatEndRef = useRef(null);


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

  function AnimatedDots() {
    const [dots, setDots] = React.useState('');
    React.useEffect(() => {
      const interval = setInterval(() => {
        setDots(d => (d.length < 3 ? d + '.' : ''));
      }, 400);
      return () => clearInterval(interval);
    }, []);
    return <span>{dots}</span>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.headerTitle}>Chat with Caze Representative</h1>
      </div>
      <div style={styles.chatArea}>
        <div style={styles.messagesArea}>
          {messages.length === 0 && (
            <div style={{ ...styles.message, background: "rgba(31, 27, 36, 0.15)", color: "#7A8FA6", textAlign: "center" }}>
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
                <Person sx={{ color: '#fff', background: 'none', borderRadius: '50%' }} />
              ) : (
                <div style={{
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  background: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: 8,
                  flexShrink: 0
                }}>
                  <img
                    src="/images/icon.png"
                    alt="Bot"
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: '50%',
                      objectFit: 'cover',
                      display: 'block'
                    }}
                  />
                </div>
              )}
              <div>
                {msg.role === "ai" ? (
                  <ReactMarkdown>{msg.message}</ReactMarkdown>
                ) : (
                  msg.message
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div style={{ 
              ...styles.loadingMessage, 
              alignSelf: "flex-start", 
              marginRight: "auto", 
              marginLeft: 0 
            }}>
              <SmartToy sx={{ color: '#7A8FA6' }} />
              <div style={{ whiteSpace: 'pre-wrap' }}>
                Generating response<AnimatedDots />
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
      </div>
      <div style={styles.inputBarWrapper}>
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