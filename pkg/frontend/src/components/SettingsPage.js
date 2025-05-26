import React, { useState } from 'react';
import EmailSettings from './EmailSettings';
import AzureSettings from './AzureSettings';
import PrivateLinkSettings from './PrivateLinkSettings';
import CompanyInfoSettings from './CompanyInfoSettings';
import LeadsInfoSettings from './LeadsInfoSettings';
import { Container, Typography, Box, Button, Tabs, Tab, createTheme, ThemeProvider, Alert, CircularProgress } from '@mui/material';

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
      main: '#BE232F',
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
    MuiTab: {
        styleOverrides: {
            root: {
                textTransform: 'none',
                fontWeight: 700,
                fontSize: '1rem',
                color: '#a0aec0',
                '&.Mui-selected': {
                    color: '#BE232F',
                },
            }
        }
    },
    MuiTabs: {
        styleOverrides: {
            indicator: {
                backgroundColor: '#BE232F',
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
            },
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
            color: '#BE232F',
          },
        },
      },
    },
  },
});

function SettingsPage() {
  const [tab, setTab] = useState('email');
  const [message, setMessage] = useState('');
  const [clearing, setClearing] = useState(false);

  const handleClearAll = async () => {
    setClearing(true);
    setMessage('');
    const res = await fetch('/api/clear-all', { method: 'POST' });
    const data = await res.json();
    setMessage(data.message);
    setClearing(false);
  };

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setMessage(''); // Clear message when changing tabs
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="md" sx={{ background: darkTheme.palette.background.default, padding: '2rem', minHeight: '100vh', color: darkTheme.palette.text.primary }}>
        <Typography variant="h2" component="h2">Settings</Typography>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', marginBottom: 3 }}>
          <Tabs value={tab} onChange={handleTabChange} aria-label="settings tabs">
            <Tab label="Email" value="email" />
            <Tab label="Azure" value="azure" />
            <Tab label="Private Link" value="private" />
            <Tab label="Company Info" value="company" />
            <Tab label="Leads Info" value="leads" />
          </Tabs>
        </Box>
        {message && <Alert severity="info" sx={{ marginBottom: 2 }}>{message}</Alert>}
        <Box>
          {tab === 'email' && <EmailSettings />}
          {tab === 'azure' && <AzureSettings />}
          {tab === 'private' && <PrivateLinkSettings />}
          {tab === 'company' && <CompanyInfoSettings />}
          {tab === 'leads' && <LeadsInfoSettings />}
        </Box>
        <Box sx={{ marginTop: 4 }}>
          <Typography variant="h5" component="h3">Clear All Data</Typography>
          <Button variant="contained" color="error" onClick={handleClearAll} disabled={clearing} startIcon={clearing ? <CircularProgress size={20} color="inherit" /> : null}>
            {clearing ? 'Clearing...' : 'Clear All'}
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default SettingsPage; 