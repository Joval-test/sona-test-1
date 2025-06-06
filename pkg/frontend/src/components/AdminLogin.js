import React, { useState } from 'react';
import { Typography, Box, TextField, Button, Alert, CircularProgress } from '@mui/material';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  card: {
    backgroundColor: "#1F1B24",
    borderRadius: "12px",
    padding: "2rem",
    boxShadow: "0 3px 8px rgba(255, 99, 71, 0.3)",
    maxWidth: "400px",
    width: "100%",
  },
  header: {
    color: "#7A8FA6",
    fontSize: "1.8rem",
    fontWeight: "700",
    marginBottom: "1.5rem",
    textAlign: "center",
  },
  input: {
    '& .MuiOutlinedInput-root': {
      backgroundColor: '#2A3B4D',
      borderRadius: '8px',
      '& fieldset': {
        borderColor: '#444',
      },
      '&:hover fieldset': {
        borderColor: '#FF6347',
      },
      '&.Mui-focused fieldset': {
        borderColor: '#FF6347',
      },
    },
    '& .MuiInputLabel-root': {
      color: '#7A8FA6',
    },
    '& .MuiOutlinedInput-input': {
      color: '#E0E0E0',
    },
  },
  button: {
    backgroundColor: "#FF6347",
    border: "none",
    padding: "0.75rem 1.5rem",
    borderRadius: "25px",
    color: "white",
    fontWeight: "600",
    cursor: "pointer",
    fontSize: "1rem",
    width: "100%",
    marginTop: "1rem",
    transition: "all 0.3s ease",
    '&:hover': {
      backgroundColor: "#FF4500",
    },
    '&:disabled': {
      opacity: 0.7,
      cursor: 'not-allowed',
    }
  }
};

function AdminLogin({ onLogin }) {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    if (!key) {
      setError('API key required');
      setLoading(false);
      return;
    }
    
    try {
      localStorage.setItem('admin_api_key', key);
      onLogin();
    } catch (err) {
      setError('Login failed');
    }
    setLoading(false);
  };

  return (
    <Box sx={styles.container}>
      <Box sx={styles.card}>
        <Typography sx={styles.header}>Admin Login</Typography>
        <Typography sx={{ 
          color: '#CCCCCC', 
          marginBottom: '2rem', 
          textAlign: 'center',
          fontSize: '0.9rem'
        }}>
          Access the administrative features to review chat histories, moderate conversations, and manage lead statuses.
        </Typography>
        
        <TextField
          label="API Key"
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          fullWidth
          sx={styles.input}
          margin="normal"
        />
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              marginTop: '1rem',
              backgroundColor: 'rgba(244, 67, 54, 0.1)',
              color: '#E0E0E0'
            }}
          >
            {error}
          </Alert>
        )}
        
        <Button
          onClick={handleLogin}
          disabled={loading}
          sx={styles.button}
        >
          {loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : 'Login'}
        </Button>
      </Box>
    </Box>
  );
}

export default AdminLogin;