import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, CircularProgress, Alert, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Checkbox, FormControlLabel, Switch, useTheme, createTheme, ThemeProvider } from '@mui/material';
import { styled } from '@mui/system';

// Dummy logo import (replace with your actual logo path if available)
// import logo from '../public/images/logo.png';

const STATUS_LIST = ['Hot', 'Warm', 'Cold', 'Not Responded'];

// Create a dark theme
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
    info: {
        main: '#e67e22', // Warm
    },
    success: {
        main: '#3498db', // Cold
    },
    warning: {
        main: '#888', // Not Responded
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
    MuiFormControlLabel: {
      styleOverrides: {
        label: {
          color: '#e2e8f0',
        },
      },
    },
    MuiSwitch: {
        styleOverrides: {
          switchBase: {
            color: '#a0aec0',
            '&.Mui-checked': {
              color: '#BE232F',
            },
            '&.Mui-checked + .MuiSwitch-track': {
              backgroundColor: '#304654',
            },
          },
          track: {
            backgroundColor: '#4a5568',
          },
        },
      },
  },
});

function getStatusCounts(leads) {
  const counts = { Total: leads.length, Hot: 0, Warm: 0, Cold: 0, 'Not Responded': 0 };
  leads.forEach(lead => {
    const status = lead['Lead Status'] || 'Not Responded';
    if (counts[status] !== undefined) counts[status]++;
  });
  return counts;
}

function safeDate(date) {
  if (!date || date === 'NaT' || date === 'null' || date === null || date === undefined) return 'Not Contacted';
  if (typeof date === 'string' && date.includes('T')) return date.split('T')[0];
  if (typeof date === 'string') return date;
  return 'Not Contacted';
}

function safeText(val, fallback = '—') {
  if (val === null || val === undefined || (typeof val === 'number' && isNaN(val))) return fallback;
  return val;
}

const MetricBox = styled(Paper)(({ theme, color }) => ({
  minWidth: 140,
  padding: '1.2rem 1.5rem',
  textAlign: 'center',
  color: color || theme.palette.text.primary,
  border: `2px solid ${color || theme.palette.text.primary}`,
  backgroundColor: theme.palette.background.paper,
  boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
}));

function ReportPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('All');
  const [detailed, setDetailed] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetch('/api/report')
      .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
      .then(data => {
        setLeads(data.leads || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.error || 'Failed to load report');
        setLoading(false);
      });
  }, []);

  const counts = getStatusCounts(leads);
  const filteredLeads = tab === 'All' ? leads : leads.filter(l => (l['Lead Status'] || 'Not Responded') === tab);
  const allNotResponded = leads.length > 0 && leads.every(l => (l['Lead Status'] || 'Not Responded') === 'Not Responded');

  // Selection logic
  const toggleSelect = idx => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx); else next.add(idx);
      return next;
    });
  };
  const selectAll = () => setSelected(new Set(filteredLeads.map((_, idx) => idx)));
  const clearSelection = () => setSelected(new Set());

  // Export selected leads to Excel
  const handleExport = async () => {
    setExporting(true);
    const XLSX = await import('xlsx');
    const selectedLeads = Array.from(selected).map(idx => filteredLeads[idx]);
    const ws = XLSX.utils.json_to_sheet(selectedLeads);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Leads');
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([wbout], { type: 'application/octet-stream' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected_leads_${new Date().toISOString().slice(0,10)}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setExporting(false);
  };

  // Delete selected leads (frontend only, for now)
  const handleDelete = () => {
    if (!window.confirm('Are you sure you want to delete the selected leads?')) return;
    setLeads(prev => prev.filter((_, idx) => !selected.has(idx)));
    setSelected(new Set());
  };

  const getStatusColor = (status) => {
    switch ((status || '').toLowerCase()) {
      case 'hot': return darkTheme.palette.primary.main; // Caze Labs Red
      case 'warm': return darkTheme.palette.info.main; // Warm
      case 'cold': return darkTheme.palette.success.main; // Cold
      case 'not responded': return darkTheme.palette.warning.main; // Not Responded
      default: return darkTheme.palette.text.primary; // Default text color
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ minHeight: '100vh', background: darkTheme.palette.background.default, padding: 0, fontFamily: darkTheme.typography.fontFamily, color: darkTheme.palette.text.primary }}>
        <Container maxWidth="lg" sx={{ padding: '2rem 2rem 2rem 2rem' }}>
          <Typography variant="h2" component="h2">Lead Engagement Dashboard</Typography>
          {loading && <CircularProgress />}
          {/* Display error if any */}
          {error && <Alert severity="error">{error}</Alert>}
          {!loading && !error && leads.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No report data found. This may be because no emails have been sent yet.
            </Alert>
          )}
          {!loading && !error && (
            leads.length === 0 ? (
              <Alert severity="info">No leads found in the report.</Alert>
            ) : allNotResponded ? (
              <Alert severity="info">No engaged leads yet. All leads are currently "Not Responded".</Alert>
            ) : (
              <>
                {/* Metrics */}
                <Box sx={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 4, marginBottom: 4 }}>
                  <Metric label="Total Leads" value={counts.Total} color={darkTheme.palette.secondary.main} />
                  <Metric label="Hot" value={counts.Hot} color={darkTheme.palette.primary.main} />
                  <Metric label="Warm" value={counts.Warm} color={darkTheme.palette.info.main} />
                  <Metric label="Cold" value={counts.Cold} color={darkTheme.palette.success.main} />
                  <Metric label="Not Responded" value={counts['Not Responded']} color={darkTheme.palette.warning.main} />
                </Box>
                {/* Tabs */}
                <Box sx={{ display: 'flex', gap: 2, marginBottom: 3, alignItems: 'center' }}>
                  {['All', ...STATUS_LIST].map(s => (
                    <Button
                      key={s}
                      variant={tab === s ? 'contained' : 'outlined'}
                      onClick={() => { setTab(s); clearSelection(); }}
                      sx={{
                        borderRadius: '16px',
                        padding: '0.6rem 2rem',
                        fontWeight: 700,
                        fontSize: '1rem',
                        borderBottom: tab === s ? '3px solid #BE232F' : '3px solid transparent',
                        background: tab === s ? 'linear-gradient(90deg, #BE232F 60%, #304654 100%)' : 'transparent',
                        color: tab === s ? '#fff' : '#BE232F',
                        borderColor: tab === s ? 'transparent' : '#BE232F',
                        '&:hover': {
                            background: tab === s ? 'linear-gradient(90deg, #BE232F 60%, #304654 100%)' : 'rgba(190, 35, 47, 0.1)', // slight hover effect for outlined
                            borderColor: tab === s ? 'transparent' : '#BE232F',
                        }
                      }}
                    >
                      {s}
                    </Button>
                  ))}
                  <FormControlLabel
                    control={<Switch checked={detailed} onChange={e => setDetailed(e.target.checked)} />}
                    label="Detailed View"
                    sx={{ marginLeft: 2 }}
                  />
                </Box>
                {/* Lead Selection Controls */}
                <Box sx={{ display: 'flex', gap: 2, marginBottom: 2, alignItems: 'center' }}>
                  <Button variant="contained" onClick={selectAll} sx={{background: darkTheme.palette.secondary.main, '&:hover': { background: darkTheme.palette.secondary.dark }}}>Select All</Button>
                  <Button variant="contained" onClick={clearSelection} sx={{background: darkTheme.palette.secondary.main, '&:hover': { background: darkTheme.palette.secondary.dark } }}>Clear Selection</Button>
                  <Typography variant="body1" sx={{ marginLeft: 2 }}>Selected: {selected.size} leads</Typography>
                </Box>
                {/* Export/Delete Buttons */}
                {selected.size > 0 && (
                  <Box sx={{ display: 'flex', gap: 2, marginBottom: 2 }}>
                    <Button variant="contained" onClick={handleExport} disabled={exporting} startIcon={exporting ? <CircularProgress size={20} color="inherit" /> : null}>
                      {exporting ? 'Exporting...' : 'Export Selected'}
                    </Button>
                    <Button variant="contained" onClick={handleDelete}>Delete Selected</Button>
                  </Box>
                )}
                {/* Lead List */}
                <Paper elevation={3} sx={{ minHeight: 200 }}>
                  {filteredLeads.length === 0 && tab !== 'All' && <Typography variant="body1" sx={{ color: darkTheme.palette.text.secondary }}>No leads in this category.</Typography>}
                  {filteredLeads.length > 0 && !detailed && (
                    <TableContainer component={Paper} sx={{ boxShadow: 'none', borderRadius: 0 }}> {/* Remove Paper's default shadow and border radius here */}
                      <Table sx={{ minWidth: 650 }} aria-label="simple table">
                        <TableHead>
                          <TableRow>
                            <TableCell padding="checkbox"></TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Company</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Last Contact</TableCell>
                            <TableCell>Chat Link</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {filteredLeads.map((lead, idx) => (
                            <TableRow
                              key={idx}
                              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            >
                              <TableCell padding="checkbox">
                                <Checkbox checked={selected.has(idx)} onChange={() => toggleSelect(idx)} />
                              </TableCell>
                              <TableCell component="th" scope="row">{safeText(lead.Name)}</TableCell>
                              <TableCell>{safeText(lead.Company)}</TableCell>
                              <TableCell>{safeText(lead.Email)}</TableCell>
                              <TableCell sx={{ color: getStatusColor(lead['Lead Status']) }}>{safeText(lead['Lead Status'])}</TableCell>
                              <TableCell>{safeDate(lead['Sent Date'])}</TableCell>
                              <TableCell>
                                {lead['Private Link'] ? (
                                  <a href={lead['Private Link']} target="_blank" rel="noopener noreferrer" style={{ color: darkTheme.palette.primary.main, textDecoration: 'underline' }}>Chat</a>
                                ) : 'N/A'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                  {filteredLeads.length > 0 && detailed && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {filteredLeads.map((lead, idx) => (
                        <Paper key={idx} elevation={2} sx={{ padding: 3, borderLeft: `6px solid ${getStatusColor(lead['Lead Status'])}` }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, marginBottom: 1 }}>
                                <Checkbox checked={selected.has(idx)} onChange={() => toggleSelect(idx)} />
                                <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: darkTheme.palette.text.primary }}>
                                    {safeText(lead.Name)}
                                    <Typography component="span" sx={{ fontWeight: 400, color: getStatusColor(lead['Lead Status']), marginLeft: 1 }}>
                                        {safeText(lead['Lead Status'])}
                                    </Typography>
                                </Typography>
                            </Box>
                          <Typography variant="body2" sx={{ marginBottom: 0.5 }}><b>Company:</b> {safeText(lead.Company)}</Typography>
                          <Typography variant="body2" sx={{ marginBottom: 0.5 }}><b>Email:</b> {safeText(lead.Email)}</Typography>
                          <Typography variant="body2" sx={{ marginBottom: 0.5 }}><b>Last Contact:</b> {safeDate(lead['Sent Date'])}</Typography>
                          <Typography variant="body2" sx={{ marginBottom: 0.5 }}><b>Summary:</b> {safeText(lead['Chat Summary'], 'No interaction yet')}</Typography>
                          <Typography variant="body2">
                            <b>Chat Link:</b> {lead['Private Link'] ? (
                              <a href={lead['Private Link']} target="_blank" rel="noopener noreferrer" style={{ color: darkTheme.palette.primary.main, textDecoration: 'underline' }}>Open Chat</a>
                            ) : 'N/A'}
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </Paper>
              </>
            )
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

function Metric({ label, value, color }) {
    const theme = useTheme();
  return (
    <MetricBox elevation={3} color={color}>
      <Typography variant="h6" component="div" sx={{ fontWeight: 700, marginBottom: 0.5 }}>{label}</Typography>
      <Typography variant="h4" component="div" sx={{ fontWeight: 900 }}>{value}</Typography>
    </MetricBox>
  );
}

export default ReportPage; 