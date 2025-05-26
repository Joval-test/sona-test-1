import React, { useState } from 'react';
import { Container, Typography, Box, TextField, Button, Alert, createTheme, ThemeProvider, CircularProgress } from '@mui/material';

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

function AdminLogin({ onLogin }) {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    if (!key) {
      setError('API key required');
      setLoading(false);
      return;
    }
    // In a real app, you'd send the key to the backend for validation
    // For this example, we'll just store it in localStorage
    localStorage.setItem('admin_api_key', key);
    // Simulate a network request
    await new Promise(resolve => setTimeout(resolve, 500));
    setLoading(false);
    onLogin();
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ background: darkTheme.palette.background.default, minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem' }}>
        <Box sx={{ maxWidth: 400, width: '100%', padding: 3, borderRadius: 2, bgcolor: darkTheme.palette.background.paper, boxShadow: 3 }}>
          <Typography variant="h4" component="h2" gutterBottom textAlign="center">Admin Login</Typography>
          <TextField
            label="Enter API Key"
            type="password"
            value={key}
            onChange={e => setKey(e.target.value)}
            fullWidth
            margin="normal"
            variant="outlined"
          />
          <Button variant="contained" onClick={handleLogin} fullWidth sx={{ marginTop: 2 }} disabled={loading} startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
          {error && <Alert severity="error" sx={{ marginTop: 2 }}>{error}</Alert>}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default AdminLogin; 