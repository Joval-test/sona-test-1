import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Input,
  createTheme,
  ThemeProvider,
  Snackbar,
} from '@mui/material';
import { useNotification } from '../hooks/useNotification';

/* ----------  DARK THEME  ---------- */
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#1a2027', paper: '#2d3748' },
    text: { primary: '#e2e8f0', secondary: '#a0aec0' },
    primary: {
      main: '#BE232F',
    },
    secondary: {
      main: '#304654',
    },
  },
  typography: { fontFamily: '"Inter","Segoe UI",Arial,sans-serif' },
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
    MuiTextField: {
      styleOverrides: {
        root: {
          '& label': { color: '#a0aec0' },
          '& label.Mui-focused': { color: '#BE232F' },
          '& .MuiInputBase-input': { color: '#e2e8f0' },
          '& .MuiOutlinedInput-root fieldset': { borderColor: '#4a5568' },
          '& .MuiOutlinedInput-root:hover fieldset': { borderColor: '#BE232F' },
          '& .MuiOutlinedInput-root.Mui-focused fieldset': { borderColor: '#BE232F' },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        h5: {
          marginBottom: '1rem',
          fontWeight: 600,
          color: '#e2e8f0',
        },
      },
    },
  },
});

/* ----------  MAIN COMPONENT  ---------- */
function CompanyInfoSettings() {
  /* state */
  const [companyFiles, setCompanyFiles] = useState([]);
  const [companyUrls, setCompanyUrls] = useState('');
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const { notification, showSuccess, showError, clearNotification } = useNotification();
  const fileInputRef = useRef(null);

  /* Accept .pdf, .doc, .docx */
  const ACCEPTED_EXTENSIONS = ['.pdf', '.doc', '.docx'];

  const isAcceptedFile = (filename) => ACCEPTED_EXTENSIONS.some(ext => filename.toLowerCase().endsWith(ext));

  /* file handlers */
  const handleSelect = (e) => {
    const files = Array.from(e.target.files || []).filter((f) => isAcceptedFile(f.name));
    if (files.length !== (e.target.files || []).length) {
      showError('Some files were rejected. Please upload only PDF, DOC, or DOCX files.');
    }
    setCompanyFiles((prev) => [...prev, ...files]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files || []).filter((f) => isAcceptedFile(f.name));
    if (files.length !== (e.dataTransfer.files || []).length) {
      showError('Some files were rejected. Please upload only PDF, DOC, or DOCX files.');
    }
    setCompanyFiles((prev) => [...prev, ...files]);
  };

  const removeFile = (indexToRemove) => {
    setCompanyFiles(companyFiles.filter((_, index) => index !== indexToRemove));
  };

  /* upload PDFs */
  const uploadCompanyFiles = async (event) => {
    event.preventDefault();
    if (!companyFiles.length) {
      showError('Please select files to upload');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      companyFiles.forEach((file) => {
        formData.append('files', file);
      });
      const res = await fetch('/api/upload/company-files', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Upload failed');
      }
      // Show success message with details
      const successCount = data.results?.filter(r => r.status === 'success').length || 0;
      const errorCount = data.results?.filter(r => r.status === 'error').length || 0;
      let message = `Successfully processed ${successCount} file${successCount !== 1 ? 's' : ''}`;
      if (errorCount > 0) {
        message += ` (${errorCount} file${errorCount !== 1 ? 's' : ''} failed)`;
      }
      showSuccess(message);
      // Reset form
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setCompanyFiles([]);
    } catch (err) {
      console.error('Upload error:', err);
      showError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  /* submit URLs */
  const submitUrls = async (event) => {
    event.preventDefault();
    if (!companyUrls.trim()) {
      showError('Please enter URLs to submit');
      return;
    }

    setSubmitting(true);
    try {
      const urls = companyUrls.split('\n').map((u) => u.trim()).filter(Boolean);
      
      const res = await fetch('/api/upload/company-urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls }),
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to submit URLs');
      }

      // Show success message with details
      const successCount = data.results?.filter(r => r.status === 'success').length || 0;
      const errorCount = data.results?.filter(r => r.status === 'error').length || 0;
      let message = `Successfully processed ${successCount} URL${successCount !== 1 ? 's' : ''}`;
      if (errorCount > 0) {
        message += ` (${errorCount} URL${errorCount !== 1 ? 's' : ''} failed)`;
      }
      showSuccess(message);
      setCompanyUrls('');
    } catch (err) {
      console.error('URL submission error:', err);
      showError(err.message || 'Failed to submit URLs. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  /* ----------  JSX  ---------- */
  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ width: '100%', position: 'relative' }}>
        {/* PDF upload form */}
        <Box component="form" onSubmit={uploadCompanyFiles} sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Upload Company Files
          </Typography>

          {/* hidden input */}
          <Input
            id="company-file-input"
            type="file"
            inputProps={{ accept: '.pdf,.doc,.docx', multiple: true }}
            sx={{ display: 'none' }}
            onChange={handleSelect}
            inputRef={fileInputRef}
          />

          {/* drag / click zone */}
          <Box
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('company-file-input')?.click()}
            sx={{
              border: `2px dashed ${
                dragOver ? darkTheme.palette.primary.main : darkTheme.palette.text.secondary
              }`,
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              mb: 2,
              backgroundColor: dragOver ? 'rgba(190, 35, 47, 0.1)' : 'rgba(255,255,255,0.03)',
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.05)',
                borderColor: darkTheme.palette.primary.main,
              },
            }}
          >
            <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>
              Drag and drop your PDF, DOC, or DOCX files here, or <strong>tap to upload</strong>
            </Typography>
            <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary }}>
              Supported formats: .pdf, .doc, .docx
            </Typography>
          </Box>

          {companyFiles.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, mb: 1 }}>
                Selected Files ({companyFiles.length}):
              </Typography>
              {companyFiles.map((file, index) => (
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

          {/* buttons right-aligned */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={uploading || !companyFiles.length}
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
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </Box>
        </Box>

        {/* URLs form */}
        <Box component="form" onSubmit={submitUrls}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Enter Company URLs
          </Typography>

          <TextField
            multiline
            rows={4}
            fullWidth
            value={companyUrls}
            onChange={(e) => setCompanyUrls(e.target.value)}
            placeholder="One URL per line"
            variant="outlined"
            sx={{ mb: 2 }}
          />

          {/* button right-aligned */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting || !companyUrls.trim()}
              startIcon={submitting ? <CircularProgress size={20} color="inherit" /> : null}
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
              {submitting ? 'Submitting...' : 'Submit URLs'}
            </Button>
          </Box>
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

export default CompanyInfoSettings;