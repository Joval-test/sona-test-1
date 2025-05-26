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
    success: {
        main: '#4caf50', // Green for success messages
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
          },        },
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
            h3: {
                marginBottom: '1rem',
                fontWeight: 600,
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
              color: '#4caf50', // Green icon for success
            },
          },
        },
      },
  },
});

function EmailSettings() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [alertState, setAlertState] = useState({ text: '', severity: 'info' });
  const [saving, setSaving] = useState(false);

  const handleEmailSettings = async e => {
    e.preventDefault();
    setSaving(true);
    setAlertState({ text: '', severity: 'info' });
    const res = await fetch('/api/settings/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender: email, password })
    });
    const data = await res.json();
    if (res.ok) {
      setAlertState({ text: 'Email settings saved successfully', severity: 'success' });
    } else {
      setAlertState({ text: data.message || 'Failed to save email settings', severity: 'error' });
    }
    setSaving(false);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box component="form" onSubmit={handleEmailSettings} sx={{ marginBottom: 3 }}>
        <Typography variant="h5" component="h3">Email Settings</Typography>
        <TextField
          label="Sender Email"
          type="email"
          placeholder="Enter sender email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <TextField
          label="Email Password"
          type="password"
          placeholder="Enter email password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <Button type="submit" variant="contained" sx={{ marginTop: 3 }} disabled={saving} startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}>
          {saving ? 'Saving...' : 'Save Email Settings'}
        </Button>
        {alertState.text && <Alert severity={alertState.severity} sx={{ marginTop: 2 }}>{alertState.text}</Alert>}
      </Box>
    </ThemeProvider>
  );
}

export default EmailSettings; 