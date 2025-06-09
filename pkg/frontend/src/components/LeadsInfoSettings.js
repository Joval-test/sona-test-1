import React, { useRef, useState } from 'react';
import {
  Typography,
  Box,
  Button,
  Alert,
  createTheme,
  ThemeProvider,
  CircularProgress,
  Input,
} from '@mui/material';

// Dark Theme
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
      main: '#BE232F',
    },
    secondary: {
      main: '#304654',
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
        h3: {
          marginBottom: '1rem',
          fontWeight: 600,
          color: '#e2e8f0',
        },
      },
    },
  },
});

function LeadsInfoSettings() {
  const [userFiles, setUserFiles] = useState([]);
  const [alertState, setAlertState] = useState({ text: '', severity: 'info' });
  const [uploading, setUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleUserFiles = async (e) => {
    e.preventDefault();
    setUploading(true);
    setAlertState({ text: '', severity: 'info' });

    const formData = new FormData();
    for (let file of userFiles) formData.append('files', file);

    const res = await fetch('/api/upload/user-files', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Upload failed');
    }

    // Show success message with details
    const successCount = data.results.filter(r => r.status === 'success').length;
    const errorCount = data.results.filter(r => r.status === 'error').length;
    const totalLeads = data.results.reduce((sum, r) => sum + (r.leads || 0), 0);
    let message = `Successfully processed ${successCount} file${successCount !== 1 ? 's' : ''} with ${totalLeads} leads`;
    if (errorCount > 0) {
      message += ` (${errorCount} file${errorCount !== 1 ? 's' : ''} failed)`;
    }
    showSuccess(message);
    setUserFiles([]);

    setUploading(false);
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
        <Typography variant="h5" component="h3">
          Upload User Data (Excel/CSV)
        </Typography>

        <input
          type="file"
          multiple
          accept=".xlsx,.xls,.csv"
          ref={inputRef}
          onChange={(e) =>
            setUserFiles((prevFiles) => [...prevFiles, ...Array.from(e.target.files)])
          }
          style={{ display: 'none' }}
        />

        <Box
          onClick={() => inputRef.current.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          sx={{
            border: `2px dashed ${
              isDragOver ? darkTheme.palette.primary.main : darkTheme.palette.text.secondary
            }`,
            borderRadius: 2,
            padding: 4,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isDragOver ? 'rgba(190, 35, 47, 0.1)' : 'rgba(255,255,255,0.03)',
            transition: 'all 0.3s ease-in-out',
            marginBottom: 2,
          }}
        >
          <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>
            Drag and drop your Excel/CSV files here, or <strong>tap to upload</strong>
          </Typography>
        </Box>

        {userFiles.length > 0 && (
          <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, mt: 1 }}>
            Selected Files: {userFiles.map((file) => file.name).join(', ')}
          </Typography>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <Button
            type="submit"
            disabled={uploading || userFiles.length === 0}
            startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : null}
            sx={{
              background: 'linear-gradient(to right, #ffffff, #3b82f6)',
              color: 'black',
              fontWeight: 700,
              borderRadius: 8,
              textTransform: 'none',
              '&:hover': {
                opacity: 0.9,
                background: 'linear-gradient(to right, #f1f1f1, #2563eb)',
              },
            }}
          >
            {uploading ? 'Uploading...' : 'Upload User Data'}
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

export default LeadsInfoSettings;
