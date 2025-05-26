import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, TextField, Button, CircularProgress, Alert, createTheme, ThemeProvider } from '@mui/material';

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
    }
  },
});

function PrivateLinkSettings() {
  const [base, setBase] = useState('');
  const [path, setPath] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/settings/private-link')
      .then(res => res.json())
      .then(data => {
        setBase(data.base || '');
        setPath(data.path || '');
        setLoading(false);
      });
  }, []);

  const handleSave = async e => {
    e.preventDefault();
    setMessage('');
    const res = await fetch('/api/settings/private-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base, path })
    });
    const data = await res.json();
    setMessage(data.message);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="sm" sx={{ background: darkTheme.palette.background.default, padding: '2rem', minHeight: '100vh' }}>
        <Box component="form" onSubmit={handleSave} sx={{ marginBottom: 3 }}>
          <Typography variant="h5" component="h3">Private Link Settings</Typography>
          <Typography variant="body1" component="label" htmlFor="base-url" display="block" sx={{ marginBottom: 0.5, color: darkTheme.palette.text.secondary }}>Base URL</Typography>
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
          <Typography variant="body1" component="label" htmlFor="path" display="block" sx={{ marginBottom: 0.5, color: darkTheme.palette.text.secondary, marginTop: 2 }}>Path</Typography>
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
          <Button type="submit" variant="contained" sx={{ marginTop: 3 }}>Save Private Link Settings</Button>
          {message && <Alert severity="success" sx={{ marginTop: 2 }}>{message}</Alert>}
        </Box>
        {loading && <CircularProgress sx={{ mt: 2 }}/>}
      </Container>
    </ThemeProvider>
  );
}

export default PrivateLinkSettings; 