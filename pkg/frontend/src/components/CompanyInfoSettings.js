import React, { useState } from 'react';
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
} from '@mui/material';

/* ----------  DARK THEME  ---------- */
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#1a2027', paper: '#2d3748' },
    text: { primary: '#e2e8f0', secondary: '#a0aec0' },
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
          backgroundImage: 'linear-gradient(90deg,#ffffff 0%,#1E88E5 100%)',
          color: '#000000',
          '&:hover': {
            opacity: 0.9,
            backgroundImage: 'linear-gradient(90deg,#ffffff 0%,#1E88E5 100%)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& label': { color: '#a0aec0' },
          '& label.Mui-focused': { color: '#3f51b5' },
          '& .MuiInputBase-input': { color: '#e2e8f0' },
          '& .MuiOutlinedInput-root fieldset': { borderColor: '#4a5568' },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          width: '90%',
          maxWidth: '600px',
          animation: 'slideDown 0.3s ease-out',
        },
      },
    },
  },
});

/* ----------  COMPONENT  ---------- */
function CompanyInfoSettings() {
  /* state */
  const [pdfFiles, setPdfFiles] = useState([]);
  const [companyUrls, setCompanyUrls] = useState('');
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const { notification, showSuccess, showError, clearNotification } = useNotification();

  /* file handlers */
  const handleSelect = (e) => {
    const files = Array.from(e.target.files || []).filter((f) =>
      f.name.toLowerCase().endsWith('.pdf')
    );
    setPdfFiles((prev) => [...prev, ...files]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files || []).filter((f) =>
      f.name.toLowerCase().endsWith('.pdf')
    );
    setPdfFiles((prev) => [...prev, ...files]);
  };

  /* upload PDFs */
  const uploadPdfs = async (e) => {
    e.preventDefault();
    if (!pdfFiles.length) return;
    setUploading(true);

    try {
      const formData = new FormData();
      pdfFiles.forEach((f) => formData.append('files', f));
      const res = await fetch('/api/upload/company-files', { method: 'POST', body: formData });
      if (!res.ok) throw new Error();

      showSuccess('Company PDFs uploaded successfully');
      setPdfFiles([]);
    } catch (err) {
      showError('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  /* submit URLs */
  const submitUrls = async (e) => {
    e.preventDefault();
    if (!companyUrls.trim()) return;
    setSubmitting(true);

    try {
      const res = await fetch('/api/upload/company-urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: companyUrls.split('\n').map((u) => u.trim()).filter(Boolean),
        }),
      });
      if (!res.ok) throw new Error();

      showSuccess('Company URLs submitted successfully');
      setCompanyUrls('');
    } catch (err) {
      showError('Submit failed');
    } finally {
      setSubmitting(false);
    }
  };

  /* ----------  JSX  ---------- */
  return (
    <ThemeProvider theme={darkTheme}>
      {notification.type && (
        <Alert severity={notification.type} onClose={clearNotification}>
          {notification.message}
        </Alert>
      )}
      <Box sx={{ width: '100%' }}>
        {/* PDF upload form */}
        <Box component="form" onSubmit={uploadPdfs} sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Upload Company PDFs
          </Typography>

          {/* hidden input */}
          <Input
            id="pdf-input"
            type="file"
            inputProps={{ accept: '.pdf', multiple: true }}
            sx={{ display: 'none' }}
            onChange={handleSelect}
          />

          {/* drag / click zone */}
          <Box
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('pdf-input').click()}
            sx={{
              border: `2px dashed ${
                dragOver ? darkTheme.palette.primary.main : darkTheme.palette.text.secondary
              }`,
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              mb: 2,
              backgroundColor: dragOver ? 'rgba(63,81,181,0.1)' : 'transparent',
              transition: 'all 0.2s',
            }}
          >
            <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>
              Drag & drop PDF files here, or click to select
            </Typography>
          </Box>

          {pdfFiles.length > 0 && (
            <Typography variant="body2" sx={{ mb: 2, color: darkTheme.palette.text.secondary }}>
              Selected PDFs:&nbsp;
              {pdfFiles.map((f) => f.name).join(', ')}
            </Typography>
          )}

          {/* buttons right-aligned */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={uploading || !pdfFiles.length}
              startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {uploading ? 'Uploading…' : 'Upload PDFs'}
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
            >
              {submitting ? 'Submitting…' : 'Submit URLs'}
            </Button>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default CompanyInfoSettings;
