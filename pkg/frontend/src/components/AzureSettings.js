import React, { useState } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  createTheme,
  ThemeProvider,
  CircularProgress,
} from '@mui/material';

// Dark theme
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
      main: '#000000', // black for save button color (overridden below)
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
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
            opacity: 0.9,
          },
        },
        containedPrimary: {
          backgroundColor: '#000000',
          color: '#fff',
          '&:hover': {
            backgroundColor: '#222222',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& label': {
            color: '#a0aec0',
            marginBottom: '-5px',
          },
          '& label.Mui-focused': {
            color: '#BE232F',
            marginBottom: '-5px',
          },
          '& .MuiInputBase-input': {
            color: '#e2e8f0',
            paddingTop: '0px',
            paddingBottom: '0px',
            height: '36px',
            lineHeight: '36px',
            fontSize: '0.875rem',
            boxSizing: 'border-box',
          },
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: '#4a5568',
              minHeight: '44px',
              borderRadius: '8px',
            },
            '&:hover fieldset': {
              borderColor: '#a0aec0',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#BE232F',
            },
          },
          marginTop: '8px',
          marginBottom: '8px',
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        h3: {
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

function AzureSettings() {
  const [azure, setAzure] = useState({
    endpoint: '',
    api_key: '',
    api_version: '',
    deployment: '',
    embedding_deployment: '',
  });
  const [alertState, setAlertState] = useState({ text: '', severity: 'info' });
  const [saving, setSaving] = useState(false);

  const handleAzureSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setAlertState({ text: '', severity: 'info' });
    const res = await fetch('/api/settings/azure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(azure),
    });
    const data = await res.json();
    if (res.ok) {
      setAlertState({ text: 'Azure settings saved successfully', severity: 'success' });
    } else {
      setAlertState({ text: data.message || 'Failed to save Azure settings', severity: 'error' });
    }
    setSaving(false);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box component="form" onSubmit={handleAzureSettings} sx={{ marginBottom: 3 }}>
        <Typography variant="h5" component="h3">
          Azure Settings
        </Typography>

        <TextField
          label="Endpoint"
          type="text"
          placeholder="e.g. https://your-resource.openai.azure.com/"
          value={azure.endpoint}
          onChange={(e) => setAzure({ ...azure, endpoint: e.target.value })}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="API Key"
          type="text"
          placeholder="Enter your API key"
          value={azure.api_key}
          onChange={(e) => setAzure({ ...azure, api_key: e.target.value })}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="API Version"
          type="text"
          placeholder="e.g. 2023-07-01-preview"
          value={azure.api_version}
          onChange={(e) => setAzure({ ...azure, api_version: e.target.value })}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="Deployment Name"
          type="text"
          placeholder="Enter your deployment name"
          value={azure.deployment}
          onChange={(e) => setAzure({ ...azure, deployment: e.target.value })}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="Embedding Deployment Name"
          type="text"
          placeholder="Enter your embedding deployment name"
          value={azure.embedding_deployment}
          onChange={(e) => setAzure({ ...azure, embedding_deployment: e.target.value })}
          fullWidth
          margin="normal"
          variant="outlined"
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', marginTop: 3 }}>
        <Button
          type="submit"
          variant="contained"
          disabled={saving}
          startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
          sx={{
            backgroundImage: 'linear-gradient(90deg, #ffffff, #1E88E5)', // white to blue
            color: '#000000', // black text
            fontWeight: 700,
            borderRadius: 2,
            textTransform: 'none',
            boxShadow: 'none',
            paddingX: 3,
            '&:hover': {
              opacity: 0.9,
              backgroundImage: 'linear-gradient(90deg, #ffffff, #1E88E5)',
            },
          }}
        >
          {saving ? 'Saving...' : 'Save Azure Settings'}
        </Button>
        </Box>

        {alertState.text && (
          <Alert severity={alertState.severity} sx={{ marginTop: 2 }}>
            {alertState.text}
          </Alert>
        )}
      </Box>
    </ThemeProvider>
  );
}

export default AzureSettings;
