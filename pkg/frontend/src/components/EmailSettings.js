import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  createTheme,
  ThemeProvider,
  CircularProgress,
} from '@mui/material';

/* ----------  THEME  ---------- */
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
      main: '#1E88E5', // blue for focus rings etc.
    },
    secondary: {
      main: '#304654',
    },
    success: {
      main: '#4caf50',
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
          padding: '6px 12px',
          fontSize: '0.9rem',
          minHeight: '36px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
            opacity: 0.92,
          },
        },
        containedPrimary: {
          background: 'linear-gradient(90deg, #ffffff 0%, #1E88E5 100%)',
          color: '#102027',
          '&:hover': {
            background: 'linear-gradient(90deg, #e0e0e0 0%, #1565C0 100%)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          marginBottom: '1rem',
          '& label': {
            color: '#a0aec0',
          },
          '& label.Mui-focused': {
            color: '#1E88E5',
          },
          '& .MuiInputBase-input': {
            color: '#e2e8f0',
            padding: '10px 12px',
            fontSize: '0.9rem',
          },
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: '#4a5568',
            },
            '&:hover fieldset': {
              borderColor: '#a0aec0',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#1E88E5',
            },
          },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        h5: {
          marginBottom: '1rem',
          fontWeight: 600,
          color: '#e2e8f0',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          backgroundColor: '#304654',
          color: '#e2e8f0',
          '.MuiAlert-icon': {
            color: '#4caf50',
          },
        },
      },
    },
  },
});

/* ----------  COMPONENT  ---------- */
function EmailSettings() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [alertInfo, setAlertInfo] = useState({ text: '', severity: 'info' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const res = await fetch('/api/settings/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender: email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to save email settings');
      }

      setSuccess('Email settings saved successfully!');
      // Optional: Clear sensitive fields after successful save
      setPassword('');
    } catch (err) {
      setError(err.message || 'Failed to save email settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess('')} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 3 }}>
        <Typography variant="h5">Email Settings</Typography>

        <TextField
          label="Sender Email"
          type="email"
          placeholder="Enter sender email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          fullWidth
          variant="outlined"
          size="small"
        />

        <TextField
          label="Email Password"
          type="password"
          placeholder="Enter email password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
          variant="outlined"
          size="small"
        />

        {/* Right-aligned button */}
        <Box display="flex" justifyContent="flex-end" mt={2}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {saving ? 'Saving…' : 'Save Email Settings'}
          </Button>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default EmailSettings;
