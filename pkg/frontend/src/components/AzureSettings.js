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
  const [errors, setErrors] = useState({});

  const handleAzureSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setAlertState({ text: '', severity: 'info' });
    setErrors({});

    try {
      const res = await fetch('/api/settings/azure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(azure),
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.message || 'Failed to save Azure settings');
      }
      
      setAlertState({ 
        text: 'Azure settings validated and saved successfully!', 
        severity: 'success' 
      });
      // Clear sensitive fields after successful save
      setAzure({
        endpoint: '',
        api_key: '',
        api_version: '',
        deployment: '',
        embedding_deployment: '',
      });
    } catch (err) {
      setAlertState({ 
        text: err.message || 'Failed to save Azure settings. Please try again.', 
        severity: 'error' 
      });
      // Set field-level errors if available
      if (err.message.includes('endpoint')) {
        setErrors(prev => ({ ...prev, endpoint: true }));
      }
      if (err.message.includes('API key')) {
        setErrors(prev => ({ ...prev, api_key: true }));
      }
      if (err.message.includes('deployment')) {
        setErrors(prev => ({ ...prev, deployment: true, embedding_deployment: true }));
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box component="form" onSubmit={handleAzureSettings} sx={{ marginBottom: 3 }}>
        <Typography variant="h5" component="h3">
          Azure Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Your credentials will be validated before saving. This may take a few seconds.
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
          required
          error={errors.endpoint}
          helperText={errors.endpoint ? "Please check your endpoint URL" : ""}
          InputProps={{
            style: { textAlign: 'center' },
          }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="API Key"
          type="password"
          value={azure.api_key}
          onChange={(e) => setAzure({ ...azure, api_key: e.target.value })}
          fullWidth
          size="small"
          required
          error={errors.api_key}
          helperText={errors.api_key ? "Please check your API key" : ""}
          sx={{ mb: 2 }}
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
          required
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
          required
          error={errors.deployment}
          helperText={errors.deployment ? "Please check your deployment name" : ""}
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
          required
          error={errors.embedding_deployment}
          helperText={errors.embedding_deployment ? "Please check your embedding deployment name" : ""}
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
              backgroundImage: 'linear-gradient(90deg, #ffffff, #1E88E5)',
              color: '#000000',
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
            {saving ? 'Validating & Saving...' : 'Save Azure Settings'}
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
