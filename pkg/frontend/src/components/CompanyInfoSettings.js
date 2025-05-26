import React, { useState } from 'react';
import { Container, Typography, Box, Button, Alert, createTheme, ThemeProvider, CircularProgress, Input, TextField } from '@mui/material';

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
    success: {
        main: '#4caf50', // Green for success messages
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
          },        },
        containedPrimary: {
            background: 'linear-gradient(90deg, #BE232F 60%, #304654 100%)',
        },
      },
    },
    MuiTextField: {
        styleOverrides: {
          root: {
            '& label': {
              color: '#a0aec0', // Secondary text color for labels
            },
            '& label.Mui-focused': {
              color: '#BE232F', // Red color when focused
            },
            '& .MuiInputBase-input': {
              color: '#e2e8f0', // Primary text color for input
            },
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#4a5568', // Darker border
              },
              '&:hover fieldset': {
                borderColor: '#a0aec0', // Lighter border on hover
              },
              '&.Mui-focused fieldset': {
                borderColor: '#BE232F', // Red border when focused
              },
            },
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
    },
    MuiAlert: {
        styleOverrides: {
          root: {
            backgroundColor: '#304654',
            color: '#e2e8f0',
            '.MuiAlert-icon': {
              color: '#4caf50', // Green icon for success
            },
          },
        },
      },
  },
});

function CompanyInfoSettings() {
  const [companyFiles, setCompanyFiles] = useState([]);
  const [companyUrls, setCompanyUrls] = useState('');
  const [fileAlertState, setFileAlertState] = useState({ text: '', severity: 'info' }); // State for file upload messages
  const [urlAlertState, setUrlAlertState] = useState({ text: '', severity: 'info' }); // State for URL submission messages
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const [submittingUrls, setSubmittingUrls] = useState(false);


  const handleCompanyFiles = async e => {
    e.preventDefault();
    setUploadingFiles(true);
    setFileAlertState({ text: '', severity: 'info' }); // Clear previous file alert
    const formData = new FormData();
    for (let file of companyFiles) formData.append('files', file);
    const res = await fetch('/api/upload/company-files', { method: 'POST', body: formData });
    const data = await res.json();
    if (res.ok) {
      setFileAlertState({ text: 'Company files uploaded successfully', severity: 'success' });
    } else {
      setFileAlertState({ text: data.message || 'Failed to upload company files', severity: 'error' });
    }
    setUploadingFiles(false);
    setCompanyFiles([]); // Clear selected files after upload
  };

  const handleCompanyUrls = async e => {
    e.preventDefault();
    setSubmittingUrls(true);
    setUrlAlertState({ text: '', severity: 'info' }); // Clear previous URL alert
    const res = await fetch('/api/upload/company-urls', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: companyUrls.split('\n').filter(url => url.trim() !== '') }) // Split by newline and filter empty lines
    });
    const data = await res.json();
    if (res.ok) {
      setUrlAlertState({ text: 'Company URLs submitted successfully', severity: 'success' });
    } else {
      setUrlAlertState({ text: data.message || 'Failed to submit company URLs', severity: 'error' });
    }
    setSubmittingUrls(false);
    setCompanyUrls(''); // Clear input after submission
  };

  return (
    <ThemeProvider theme={darkTheme}>
        <Box>
          <Box component="form" onSubmit={handleCompanyFiles} sx={{ marginBottom: 3 }}>
            <Typography variant="h5" component="h3">Upload Company PDFs</Typography>
            <Input
                type="file"
                multiple
                accept=".pdf"
                onChange={e => setCompanyFiles(Array.from(e.target.files))}
                sx={{ display: 'none' }}
                id="pdf-upload"
            />
            <label htmlFor="pdf-upload">
                <Button variant="contained" component="span" sx={{ marginRight: 2 }}>
                    Select PDFs
                </Button>
            </label>
            {companyFiles.length > 0 && (
                <Typography variant="body2" sx={{ color: darkTheme.palette.text.secondary, display: 'inline-block' }}>
                    Selected Files: {companyFiles.map(file => file.name).join(', ')}
                </Typography>
            )}
            <Button type="submit" variant="contained" disabled={uploadingFiles || companyFiles.length === 0} startIcon={uploadingFiles ? <CircularProgress size={20} color="inherit" /> : null}>
              {uploadingFiles ? 'Uploading...' : 'Upload PDFs'}
            </Button>
          </Box>

          <Box component="form" onSubmit={handleCompanyUrls} sx={{ marginBottom: 3 }}>
            <Typography variant="h5" component="h3">Enter Company URLs</Typography>
            <TextField
                multiline
                rows={4}
                fullWidth
                value={companyUrls}
                onChange={e => setCompanyUrls(e.target.value)}
                placeholder="One URL per line"
                variant="outlined"
                sx={{ marginBottom: 2 }}
            />
            <Button type="submit" variant="contained" disabled={submittingUrls || companyUrls.trim() === ''} startIcon={submittingUrls ? <CircularProgress size={20} color="inherit" /> : null}>
              {submittingUrls ? 'Submitting...' : 'Submit URLs'}
            </Button>
          </Box>

          {fileAlertState.text && <Alert severity={fileAlertState.severity} sx={{ marginTop: 2 }}>{fileAlertState.text}</Alert>}
          {urlAlertState.text && <Alert severity={urlAlertState.severity} sx={{ marginTop: 2 }}>{urlAlertState.text}</Alert>}
        </Box>
    </ThemeProvider>
  );
}
export default CompanyInfoSettings; 