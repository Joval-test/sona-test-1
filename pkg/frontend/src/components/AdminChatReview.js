import React, { useState } from 'react';
import { Container, Typography, Box, TextField, Button, Alert, createTheme, ThemeProvider, CircularProgress, Paper, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

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
    success: {
        main: '#4caf50', // Green for success messages
    },
    error: {
        main: '#f44336', // Red for error messages
    }
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
          '\&:hover': {
            boxShadow: 'none',
            opacity: 0.9,
          },
        },
        containedPrimary: {
            background: 'linear-gradient(90deg, #BE232F 60%, #1E88E5 100%)',
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
    MuiTypography: {
        styleOverrides: {
            h2: {
                marginBottom: '1.5rem',
                fontWeight: 700,
                letterSpacing: '-0.5px',
                color: '#e2e8f0',
            },
            h3: {
                marginBottom: '1rem',
                fontWeight: 600,
                color: '#e2e8f0',
            }
        }
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
    MuiSelect: {
        styleOverrides: {
            select: {
                color: '#e2e8f0',
            },
            icon: {
                color: '#e2e8f0',
            },
            outlined: {
                borderColor: '#4a5568',
                '&:hover fieldset': {
                  borderColor: '#a0aec0',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#BE232F',
                },
            },
        }
    },
    MuiInputLabel: {
        styleOverrides: {
            root: {
                color: '#a0aec0',
                '&.Mui-focused': {
                    color: '#BE232F',
                },
            }
        }
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          width: '90%',
          maxWidth: '600px',
          animation: 'slideDown 0.3s ease-out',
        },
      },
    },
  },
});

function AdminChatReview() {
  const { notification, showSuccess, showError } = useNotification();
  const [uuid, setUuid] = useState('');
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState('');
  const [summary, setSummary] = useState('');
  const [contact, setContact] = useState('');
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [markingLead, setMarkingLead] = useState(false);

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const apiKey = localStorage.getItem('admin_api_key');
      if (!apiKey) throw new Error();
      
      const res = await fetch(`/api/admin/chat_history/${uuid}`, {
        headers: { 'X-API-KEY': apiKey }
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setHistory(data.history || []);
    } catch (err) {
      showError();
    } finally {
      setLoadingHistory(false);
    }
  };

  const markLead = async () => {
    setMarkingLead(true);
    try {
      const apiKey = localStorage.getItem('admin_api_key');
      if (!apiKey) throw new Error();
      
      const res = await fetch('/api/admin/mark_lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
        body: JSON.stringify({ uuid, status, summary, contact })
      });
      if (!res.ok) throw new Error();
      showSuccess();
    } catch (err) {
      showError();
    } finally {
      setMarkingLead(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="sm" sx={{ background: darkTheme.palette.background.default, padding: '2rem', minHeight: '100vh', color: darkTheme.palette.text.primary }}>
        {notification.type && (
          <Alert severity={notification.type} onClose={clearNotification}>
            {notification.message}
          </Alert>
        )}
        
        <Typography variant="h4" component="h2" gutterBottom>Admin Chat Review</Typography>
        <Box sx={{ display: 'flex', gap: 2, marginBottom: 3 }}>
          <TextField
            label="Enter Lead UUID"
            variant="outlined"
            value={uuid}
            onChange={e => setUuid(e.target.value)}
            fullWidth
            size="small"
          />
          <Button variant="contained" onClick={fetchHistory} disabled={loadingHistory} startIcon={loadingHistory ? <CircularProgress size={20} color="inherit" /> : null}>
            {loadingHistory ? 'Fetching...' : 'Fetch Chat'}
          </Button>
        </Box>

        <Paper sx={{ minHeight: 200, padding: 2, marginBottom: 3, overflowY: 'auto' }}>
          {history.length === 0 ? (
            <Typography variant="body2" color="textSecondary">No chat history found.</Typography>
          ) : (
            history.map((msg, i) => (
              <Box key={i} sx={{
                textAlign: msg.role === 'user' ? 'right' : 'left',
                margin: 1,
                color: msg.role === 'user' ? darkTheme.palette.text.primary : darkTheme.palette.primary.main // Use theme colors
              }}>
                <Typography variant="body2" component="span" sx={{ fontWeight: 'bold' }}>{msg.role === 'user' ? 'User' : 'Caze Rep'}:</Typography>
                <Typography variant="body2" component="span" sx={{ marginLeft: 0.5 }}>{msg.message}</Typography>
              </Box>
            ))
          )}
        </Paper>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth size="small">
                <InputLabel id="status-select-label">Select Status</InputLabel>
                <Select
                    labelId="status-select-label"
                    id="status-select"
                    value={status}
                    label="Select Status"
                    onChange={e => setStatus(e.target.value)}
                >
                    <MenuItem value="">Select Status</MenuItem>
                    <MenuItem value="Hot">Hot</MenuItem>
                    <MenuItem value="Warm">Warm</MenuItem>
                    <MenuItem value="Cold">Cold</MenuItem>
                </Select>
            </FormControl>

          <TextField
            label="Summary"
            variant="outlined"
            value={summary}
            onChange={e => setSummary(e.target.value)}
            fullWidth
            size="small"
          />
          <TextField
            label="Contact Info"
            variant="outlined"
            value={contact}
            onChange={e => setContact(e.target.value)}
            fullWidth
            size="small"
          />

          <Button variant="contained" onClick={markLead} disabled={markingLead || !uuid || !status} startIcon={markingLead ? <CircularProgress size={20} color="inherit" /> : null}>
            {markingLead ? 'Marking...' : 'Mark Lead'}
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default AdminChatReview;