import React, { useEffect, useState } from 'react';
import { Typography, Box, CircularProgress } from '@mui/material';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  header: {
    color: "#7A8FA6",
    fontSize: "2rem",
    fontWeight: "700",
    marginBottom: "1.5rem",
  },
  card: {
    backgroundColor: "#1F1B24",
    borderRadius: "12px",
    padding: "2rem",
    boxShadow: "0 3px 8px rgba(255, 99, 71, 0.3)",
    textAlign: "center",
  }
};

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
    <Box sx={styles.container}>
      <Typography sx={styles.header}>User Dashboard</Typography>
      
      <Box sx={styles.card}>
        {loading ? (
          <CircularProgress sx={{ color: '#FF6347' }} />
        ) : (
          <Typography variant="h6" sx={{ color: '#E0E0E0' }}>
            {message}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

export default UserDashboard;