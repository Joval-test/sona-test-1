import React, { useState, useEffect, useRef } from 'react';
import { Container, Typography, Box, TextField, Button, Paper, Alert, createTheme, ThemeProvider } from '@mui/material';

// Create a dark theme (can be shared across components)
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#1a2027',
      paper: '#2d3748',
    },
    text: {
      primary: '#e2e8f0',
      secondary: '#a0aec0',
    },
    primary: {
      main: '#BE232F', // Caze Labs Red
    },
    secondary: {
      main: '#304654', // Caze Labs Dark Blue
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", Arial, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontWeight: 700,
          borderRadius: 8,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
            opacity: 0.9,
          },
        },
        containedPrimary: {
            background: 'linear-gradient(90deg, #BE232F 60%, #304654 100%)',
        },
      },
    },
    MuiTextField: {
        styleOverrides: {
          root: {
            '& label': {
              color: '#a0aec0', // Secondary text color for labels
            },
            '& label.Mui-focused': {
              color: '#BE232F', // Red color when focused
            },
            '& .MuiInputBase-input': {
              color: '#e2e8f0', // Primary text color for input
            },
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#4a5568', // Darker border
              },
              '&:hover fieldset': {
                borderColor: '#a0aec0', // Lighter border on hover
              },
              '&.Mui-focused fieldset': {
                borderColor: '#BE232F', // Red border when focused
              },
            },
          },
        },
      },
    MuiPaper: {
        styleOverrides: {
            root: {
                padding: 16,
                borderRadius: 8,
                boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
                backgroundColor: '#2d3748', // Match paper background
            }
        }
    },
    MuiTypography: {
        styleOverrides: {
            h2: {
                marginBottom: '1.5rem',
                fontWeight: 700,
                letterSpacing: '-0.5px',
                color: '#e2e8f0',
            }
        }
    },
    MuiAlert: {
        styleOverrides: {
          root: {
            backgroundColor: '#304654',
            color: '#e2e8f0',
            '.MuiAlert-icon': {
              color: '#f44336', // Red icon for error
            },
          },
        },
      },
  },
});

function UserChat() {
  const params = new URLSearchParams(window.location.search);
  const uuid = params.get('user');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: 'user', message: input }]);
    setInput('');
    try {
      const res = await fetch(`/api/user_chat/${uuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setMessages(msgs => [...msgs, { role: 'ai', message: data.response }]);
      }
    } catch (e) {
      setError('Network error');
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="sm" sx={{ background: darkTheme.palette.background.default, minHeight: '100vh', padding: '2rem', color: darkTheme.palette.text.primary }}>
        <Typography variant="h4" component="h2" gutterBottom>Chat with Us</Typography>
        <Paper sx={{
          minHeight: 300, padding: 2, marginBottom: 2,
          overflowY: 'auto', display: 'flex', flexDirection: 'column',
          gap: 1
        }}>
          {messages.map((msg, i) => (
            <Box key={i} sx={{
              textAlign: msg.role === 'user' ? 'right' : 'left',
              margin: 0,
              color: msg.role === 'user' ? darkTheme.palette.text.primary : darkTheme.palette.primary.main
            }}>
              <Typography component="span" sx={{ fontWeight: 'bold' }}>{msg.role === 'user' ? 'You' : 'Caze Rep'}:</Typography>
              <Typography component="span" sx={{ marginLeft: 0.5 }}>{msg.message}</Typography>
            </Box>
          ))}
          <div ref={chatEndRef} />
        </Paper>
        {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            value={input}
            onChange={e => setInput(e.target.value)}
            sx={{ flexGrow: 1 }}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            variant="outlined"
            size="small"
          />
          <Button variant="contained" onClick={sendMessage}>Send</Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default UserChat; 