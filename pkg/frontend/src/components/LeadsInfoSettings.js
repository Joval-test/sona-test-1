import React, { useRef, useState } from 'react';
import {
  Typography,
  Box,
  Button,
  Alert,
  createTheme,
  ThemeProvider,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import { useNotification } from '../hooks/useNotification';

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
  const [uploading, setUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const { notification, showSuccess, showError, clearNotification } = useNotification();
  const inputRef = useRef(null);

  const handleUserFiles = async (e) => {
    e.preventDefault();
    setUploading(true);

    try {
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
      
      // Extract lead count from the message string
      const totalLeads = data.results.reduce((sum, r) => {
        if (r.status === 'success' && r.message) {
          // Extract number from message like "Successfully processed 3 leads from Leads.xlsx"
          const match = r.message.match(/processed (\d+) leads/);
          const leadsCount = match ? parseInt(match[1], 10) : 0;
          return sum + leadsCount;
        }
        return sum;
      }, 0);
      
      let message = `Successfully processed ${successCount} file${successCount !== 1 ? 's' : ''}`;
      if (totalLeads > 0) {
        message += ` with ${totalLeads} leads`;
      }
      if (errorCount > 0) {
        message += ` (${errorCount} file${errorCount !== 1 ? 's' : ''} failed)`;
      }
      
      showSuccess(message);
      setUserFiles([]);
      
      // Clear file input
      if (inputRef.current) {
        inputRef.current.value = '';
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      showError(error.message || 'Failed to upload files. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => 
      file.type.includes('csv') || 
      file.type.includes('excel') || 
      file.type.includes('spreadsheet') ||
      file.name.endsWith('.csv') ||
      file.name.endsWith('.xlsx') ||
      file.name.endsWith('.xls')
    );
    
    if (validFiles.length !== files.length) {
      showError('Some files were rejected. Please upload only Excel (.xlsx, .xls) or CSV files.');
    }
    
    setUserFiles(validFiles);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files);
    setUserFiles((prevFiles) => [...prevFiles, ...files]);
  };

  const removeFile = (indexToRemove) => {
    setUserFiles(userFiles.filter((_, index) => index !== indexToRemove));
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
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        <Box
          onClick={() => inputRef.current?.click()}
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
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.05)',
              borderColor: darkTheme.palette.primary.main,
            },
          }}
        >
          <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>
            Drag and drop your Excel/CSV files here, or <strong>tap to upload</strong>
          </Typography>
          <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, mt: 1, fontSize: '0.875rem' }}>
            Supported formats: .xlsx, .xls, .csv
          </Typography>
        </Box>

        {userFiles.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, mb: 1 }}>
              Selected Files ({userFiles.length}):
            </Typography>
            {userFiles.map((file, index) => (
              <Box 
                key={index} 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  padding: 1,
                  borderRadius: 1,
                  mb: 1
                }}
              >
                <Typography variant="body2" sx={{ color: darkTheme.palette.text.primary }}>
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </Typography>
                <Button
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  sx={{ 
                    color: darkTheme.palette.error?.main || '#f56565',
                    minWidth: 'auto',
                    padding: '4px 8px'
                  }}
                >
                  Remove
                </Button>
              </Box>
            ))}
          </Box>
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
              '&:disabled': {
                opacity: 0.6,
                background: 'linear-gradient(to right, #cccccc, #9ca3af)',
              },
            }}
          >
            {uploading ? 'Uploading...' : 'Upload User Data'}
          </Button>
        </Box>

        {/* Success/Error Notification Snackbar */}
        <Snackbar
          open={!!notification.message}
          autoHideDuration={6000}
          onClose={clearNotification}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert 
            onClose={clearNotification} 
            severity={notification.type === 'success' ? 'success' : 'error'}
            sx={{ 
              width: '100%',
              '& .MuiAlert-message': {
                fontSize: '0.875rem'
              }
            }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default LeadsInfoSettings;