import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  createTheme,
  ThemeProvider
} from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#BE232F' },
    secondary: { main: '#304654' },
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
          padding: '0.6rem 0.6rem',
          background: 'linear-gradient(90deg, #ffffff 0%, #1E88E5 100%)',
          color: '#000000',
          '&:hover': {
            opacity: 0.9,
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-input': {
            padding: '10px 14px',
            textAlign: 'left', // Ensure left-aligned placeholder/input
          },
        },
      },
    },
  },
});

function PrivateLinkSettings() {
  const [base, setBase] = useState('');
  const [path, setPath] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('/api/settings/private-link')
      .then(res => res.json())
      .then(data => {
        if (data && data.config) {
          setBase(data.config.base || '');
          setPath(data.config.path || '');
        }
      })
      .catch(error => {
        console.error('Error fetching settings:', error);
      });
  }, []);

  const handleSave = async e => {
    e.preventDefault();
    setMessage('');
    const res = await fetch('/api/settings/private-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base, path }),
    });
    const data = await res.json();
    setMessage({ text: data.message, success: data.success });
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          minHeight: '50vh',
          width: '100%',
          p: 4,
          boxSizing: 'border-box',
          backgroundColor: 'transparent',
        }}
      >
        <Box
          component="form"
          onSubmit={handleSave}
          sx={{ width: '100%', maxWidth: '100%' }}
        >
          <Typography variant="h5" sx={{ mb: 2 }}>
            Private Link Settings
          </Typography>

          <Typography
            variant="body1"
            component="label"
            htmlFor="base-url"
            sx={{ mb: 1, display: 'block' }}
          >
            Base URL
          </Typography>

          <TextField
            id="base-url"
            type="text"
            placeholder="e.g. https://yourdomain.com"
            value={base}
            onChange={e => setBase(e.target.value)}
            fullWidth
            margin="normal"
            variant="outlined"
          />

          <Typography
            variant="body1"
            component="label"
            htmlFor="path"
            sx={{ mt: 2, mb: 1, display: 'block' }}
          >
            Path
          </Typography>

          <TextField
            id="path"
            type="text"
            placeholder="e.g. /chat?user="
            value={path}
            onChange={e => setPath(e.target.value)}
            fullWidth
            margin="normal"
            variant="outlined"
          />

          {/* Right-aligned button */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button type="submit" variant="contained">
              Save Private Link Settings
            </Button>
          </Box>

          {message && (
            <Alert severity={message.success === false ? 'error' : 'success'} sx={{ mt: 2 }}>
              {message.text}
            </Alert>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default PrivateLinkSettings;
