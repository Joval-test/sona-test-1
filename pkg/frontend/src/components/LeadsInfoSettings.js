import React, { useState } from 'react';
import { Container, Typography, Box, Button, Alert, createTheme, ThemeProvider, CircularProgress, Input } from '@mui/material';

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

function LeadsInfoSettings() {
  const [userFiles, setUserFiles] = useState([]);
  const [alertState, setAlertState] = useState({ text: '', severity: 'info' });
  const [uploading, setUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleUserFiles = async e => {
    e.preventDefault();
    setUploading(true);
    setAlertState({ text: '', severity: 'info' });
    const formData = new FormData();
    for (let file of userFiles) formData.append('files', file);
    const res = await fetch('/api/upload/user-files', { method: 'POST', body: formData });
    const data = await res.json();
    if (res.ok) {
      setAlertState({ text: 'Files uploaded successfully', severity: 'success' });
    } else {
      setAlertState({ text: data.message || 'Failed to upload files', severity: 'error' });
    }
    setUploading(false);
    setUserFiles([]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    setUserFiles(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box component="form" onSubmit={handleUserFiles} sx={{ marginBottom: 3 }}>
        <Typography variant="h5" component="h3">Upload User Data (Excel/CSV)</Typography>
        <Input
            type="file"
            multiple
            accept=".xlsx,.xls,.csv"
            onChange={e => setUserFiles(prevFiles => [...prevFiles, ...Array.from(e.target.files)])}
            sx={{ display: 'none' }}
            id="file-upload"
        />

        <Box
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          sx={{
            border: `2px dashed ${isDragOver ? darkTheme.palette.primary.main : darkTheme.palette.text.secondary}`,
            borderRadius: 2,
            padding: 4,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragOver ? 'rgba(190, 35, 47, 0.1)' : 'transparent',
            transition: 'border-color 0.3s ease-in-out, background-color 0.3s ease-in-out',
            marginBottom: 2
          }}
        >
          <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>
            Drag and drop your Excel/CSV files here, or
          </Typography>
          <Button variant="contained" component="label" htmlFor="file-upload" sx={{ marginTop: 1 }}>
              Select Files
          </Button>
        </Box>

        {userFiles.length > 0 && (
            <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, mt: 1 }}>
                Selected Files: {userFiles.map(file => file.name).join(', ')}
            </Typography>
        )}
        <Button type="submit" variant="contained" disabled={uploading || userFiles.length === 0} startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : null}>
          {uploading ? 'Uploading...' : 'Upload User Data'}
        </Button>
        {alertState.text && <Alert severity={alertState.severity} sx={{ marginTop: 2 }}>{alertState.text}</Alert>}
      </Box>
    </ThemeProvider>
  );
}

export default LeadsInfoSettings; 