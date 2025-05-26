import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Typography, Box, Button, createTheme, ThemeProvider } from '@mui/material';

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
          '&:hover': {
            boxShadow: 'none',
            opacity: 0.9,
          },
        },
        containedPrimary: {
            background: 'linear-gradient(90deg, #BE232F 60%, #304654 100%)',
        },
      },
    },
    MuiTypography: {
        styleOverrides: {
            h1: {
                marginBottom: '1rem',
                fontWeight: 700,
                letterSpacing: '-0.5px',
                color: '#e2e8f0',
            },
            body1: {
                marginBottom: '1.5rem',
                color: '#a0aec0',
            }
        }
    },
  },
});

function LandingPage() {
  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ minHeight: '100vh', background: darkTheme.palette.background.default, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '2rem' }}>
        <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
          <Typography variant="h2" component="h1">Welcome to Caze Labs</Typography>
          <Typography variant="body1">
            Revolutionizing Lead Management and Business Communication with AI-powered tools. Upload, connect, and manage your business leads and company info with ease.
          </Typography>
          <Button variant="contained" component={Link} to="/connect">
            Go to Connect Page
          </Button>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default LandingPage; 