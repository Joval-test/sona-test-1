import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, CircularProgress, createTheme, ThemeProvider } from '@mui/material';

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
  },
});

function UserDashboard() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/user')
      .then(res => res.json())
      .then(data => {
        setMessage(data.message);
        setLoading(false);
      })
      .catch(() => {
        setMessage('Failed to load message.');
        setLoading(false);
      });
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="md" sx={{ background: darkTheme.palette.background.default, minHeight: '100vh', padding: '2rem', color: darkTheme.palette.text.primary }}>
        <Typography variant="h4" component="h2" gutterBottom>User Dashboard</Typography>
        <Box>
          {loading ? (
            <CircularProgress />
          ) : (
            <Typography variant="body1">{message}</Typography>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default UserDashboard; 