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
  const [email, setEmail] = useState({ sender: '', password: '' });
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
        body: JSON.stringify({ sender: email.sender, password: email.password }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || 'Failed to save email settings');
      }

      setSuccess('Email settings validated and saved successfully!');
      // Optional: Clear sensitive fields after successful save
      setEmail({ sender: '', password: '' });
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
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Your credentials will be validated before saving. This may take a few seconds.
        </Typography>

        <TextField
          label="Sender Email"
          type="email"
          placeholder="Enter sender email"
          value={email.sender}
          onChange={(e) => setEmail({ ...email, sender: e.target.value })}
          fullWidth
          variant="outlined"
          size="small"
          required
          error={!!error}
          helperText={error ? "Please check your email address" : ""}
        />

        <TextField
          label="Email Password"
          type="password"
          value={email.password}
          onChange={(e) => setEmail({ ...email, password: e.target.value })}
          fullWidth
          size="small"
          sx={{ mb: 2 }}
          required
          error={!!error}
          helperText={error ? "Please check your password" : ""}
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
            {saving ? 'Validating & Saving...' : 'Save Email Settings'}
          </Button>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default EmailSettings;
