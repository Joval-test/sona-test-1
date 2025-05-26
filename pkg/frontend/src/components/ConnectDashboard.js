import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, CircularProgress, Alert, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Checkbox, useTheme, createTheme, ThemeProvider } from '@mui/material';
import { styled } from '@mui/system';

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
        main: '#3498db', // Sent (using blue for visibility in dark mode)
    },
    error: {
        main: '#BE232F', // Failed (using red)
    },
    warning: {
        main: '#e67e22', // Cooldown (using orange)
    },
    info: {
        main: '#a0aec0', // No Content, Not Sent (using secondary text color)
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
          '&:hover': {
            boxShadow: 'none',
            opacity: 0.9,
          },
        },
        containedPrimary: {
            background: 'linear-gradient(90deg, #BE232F 60%, #304654 100%)',
        },
        outlined: {
            borderColor: '#BE232F',
            color: '#BE232F',
            '&:hover': {
                borderColor: '#BE232F',
                opacity: 0.9,
            },
        },
      },
    },
    MuiPaper: {
        styleOverrides: {
            root: {
                padding: 32,
                borderRadius: 16,
                boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
            }
        }
    },
    MuiTableContainer: {
        styleOverrides: {
            root: {
                borderRadius: 16,
                boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
                background: '#2d3748', // Match paper background
            }
        }
    },
    MuiTableHead: {
        styleOverrides: {
            root: {
                backgroundColor: '#1a2027', // Match default background
            }
        }
    },
    MuiTableCell: {
        styleOverrides: {
            root: {
                borderColor: '#4a5568', // Darker border for separation
                color: '#e2e8f0', // Primary text color
            }
        }
    },
    MuiTypography: {
        styleOverrides: {
            h2: {
                marginBottom: '1.5rem',
                fontWeight: 700,
                letterSpacing: '-0.5px',
                color: '#e2e8f0',
            },
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
            color: '#BE232F',
          },
        },
      },
    },
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: '#BE232F',
          '&.Mui-checked': {
            color: '#BE232F',
          },
        },
      },
    },
  },
});

const cellStyle = { textAlign: 'left', padding: '10px 8px' };

function AdminDashboard() {
  const [leadsBySource, setLeadsBySource] = useState({});
  const [selected, setSelected] = useState({}); // {leadId: true/false}
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/leads')
      .then(res => res.json())
      .then(data => {
        setLeadsBySource(data);
        setLoading(false);
      })
      .catch(err => {
         console.error('Failed to load leads:', err);
         setLoading(false);
      });
  }, []);

  const handleSelectAll = (source) => {
    const newSelected = { ...selected };
    leadsBySource[source].forEach(lead => {
      newSelected[lead.id] = true;
    });
    setSelected(newSelected);
  };

  const handleClearAll = (source) => {
    const newSelected = { ...selected };
    leadsBySource[source].forEach(lead => {
      newSelected[lead.id] = false;
    });
    setSelected(newSelected);
  };

  const handleCheckbox = (leadId, checked) => {
    setSelected({ ...selected, [leadId]: checked });
  };

  const handleSendEmails = async () => {
    setSending(true);
    setResult(null);
    const leadIds = Object.keys(selected).filter(id => selected[id]).map(Number);
    const res = await fetch('/api/send_emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_ids: leadIds })
    });
    const data = await res.json();
    setResult(data);
    setSending(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
        case 'sent': return darkTheme.palette.success.main;
        case 'error': return darkTheme.palette.error.main;
        case 'cooldown': return darkTheme.palette.warning.main;
        case 'no_content': return darkTheme.palette.info.main;
        default: return darkTheme.palette.info.main; // Not Sent
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Container maxWidth="lg" sx={{ padding: '2rem 2rem 2rem 2rem', background: darkTheme.palette.background.default, minHeight: '100vh' }}>
        <Typography variant="h2" component="h2">Admin Dashboard</Typography>
        <Box sx={{ marginBottom: 3 }}>
          {loading && <CircularProgress />}
          {!loading && Object.keys(leadsBySource).length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No leads found. Please go to Settings &gt; Leads Info Settings to upload lead information.
            </Alert>
          )}
          <Box sx={{ display: 'flex', gap: 2 }}>
            {Object.keys(leadsBySource).map(source => (
              <Button key={source} variant={result === source ? 'contained' : 'outlined'} onClick={() => setResult(source)}>{source}</Button>
            ))}
          </Box>
        </Box>
        {Object.keys(leadsBySource).map(source => (
          <Box key={source} sx={{ marginBottom: 4 }}>
            <Typography variant="h3" component="h3">{source} Leads</Typography>
            <Button variant="contained" onClick={() => handleSelectAll(source)} sx={{ marginRight: 1, background: darkTheme.palette.secondary.main, '&:hover': { background: darkTheme.palette.secondary.dark } }}>Select All</Button>
            <Button variant="contained" onClick={() => handleClearAll(source)} sx={{background: darkTheme.palette.secondary.main, '&:hover': { background: darkTheme.palette.secondary.dark } }}>Clear All</Button>
            <TableContainer component={Paper} sx={{ marginTop: 2, boxShadow: 'none', borderRadius: 0 }}>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">Select</TableCell>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Company</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Email Sent Count</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leadsBySource[source].map(lead => (
                    <TableRow key={lead.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={!!selected[lead.id]}
                          onChange={e => handleCheckbox(lead.id, e.target.checked)}
                        />
                      </TableCell>
                      <TableCell>{lead.id}</TableCell>
                      <TableCell>{lead.name}</TableCell>
                      <TableCell>{lead.company}</TableCell>
                      <TableCell>{lead.description}</TableCell>
                      <TableCell sx={{ color: getStatusColor(lead.email_sent ? 'sent' : 'not_sent') }}>{lead.email_sent ? 'Sent' : 'Not Sent'}</TableCell>
                      <TableCell>{lead.email_sent_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        ))}
        <Button variant="contained" onClick={handleSendEmails} disabled={sending} sx={{ marginTop: 2 }} startIcon={sending ? <CircularProgress size={20} color="inherit" /> : null}>
          {sending ? 'Sending...' : 'Send Email to Selected Leads'}
        </Button>
        {result && (
          <Paper elevation={3} sx={{ marginTop: 3, padding: 2, maxWidth: 500 }}>
            <Typography variant="h6" component="h4" sx={{ marginBottom: 1 }}>Send Results</Typography>
            <Box component="ul" sx={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {(() => {
                const sent = result.results.filter(r => r.status === 'sent').length;
                const failed = result.results.filter(r => r.status === 'error').length;
                const cooldown = result.results.filter(r => r.status === 'cooldown').length;
                const noContent = result.results.filter(r => r.status === 'no_content').length;
                return (
                  <>
                    <Typography component="li" sx={{ color: sent > 0 ? darkTheme.palette.success.main : darkTheme.palette.text.primary }}>✅ Sent: {sent}</Typography>
                    <Typography component="li" sx={{ color: failed > 0 ? darkTheme.palette.error.main : darkTheme.palette.text.primary }}>❌ Failed: {failed}</Typography>
                    <Typography component="li" sx={{ color: darkTheme.palette.warning.main }}>⏳ Cooldown: {cooldown}</Typography>
                    <Typography component="li" sx={{ color: darkTheme.palette.info.main }}>⚠️ No Content: {noContent}</Typography>
                  </>
                );
              })()}
            </Box>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default AdminDashboard; 