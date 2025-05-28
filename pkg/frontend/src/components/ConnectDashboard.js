import React, { useEffect, useState } from 'react';

// Add a new centered table cell style to the styles object
const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  topBar: {

    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginBottom: "1.5rem",
  },
  header: {
    color: "#7A8FA6",
    fontSize: "2.5rem",
    fontWeight: "700",
    textAlign: "center",
    marginBottom: "1rem",
  },
  searchContainer: {
    width: "100%",
    display: "flex",
    justifyContent: "flex-end",
  },
  searchInput: {
    padding: "0.5rem 1rem",
    borderRadius: "20px",
    border: "1px solid #444",
    backgroundColor: "#1E1E1E",
    color: "#E0E0E0",
    outline: "none",
    fontSize: "0.9rem",
    width: "250px",
  },
  card: {
    backgroundColor: "#1F1B24",
    borderRadius: "12px",
    padding: "0.8rem 1rem",
    boxShadow: "0 3px 8px rgba(33, 150, 243, 0.3)",
    display: "flex",
    flexDirection: "column",
    gap: "0.6rem",
    marginBottom: "1rem",
    cursor: "pointer",
    width: "100%",
    boxSizing: "border-box",
  },
  headerLine: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontWeight: "700",
    color: "#7A8FA6",
    fontSize: "1rem",
    gap: "1rem",
    flexWrap: "wrap",
    width: "100%",
  },
  headerItem: {
    flex: "1 1 auto",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    textAlign: "left",
  },
  expandedContent: {
    marginTop: "0.6rem",
    borderTop: "1px solid #444",
    paddingTop: "0.6rem",
    fontSize: "0.85rem",
    color: "#CCCCCC",
    lineHeight: "1.3",
  },
  actionButton: {
    backgroundColor: "#2196F3",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "20px",
    color: "white",
    fontWeight: "600",
    cursor: "pointer",
    fontSize: "0.9rem",
    margin: "0.5rem 0.5rem 0.5rem 0",
    transition: "all 0.3s ease",
  },
  statusBadge: {
    padding: "0.25rem 0.8rem",
    borderRadius: "15px",
    fontSize: "0.85rem",
    fontWeight: "600",
    whiteSpace: "nowrap",
  },
  tableHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.75rem 0',
    borderBottom: '2px solid #2196F3',
    marginBottom: '0.5rem',
    fontWeight: 'bold',
    color: '#2196F3',
    fontSize: '0.9rem',
  },
  tableRow: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.5rem 0',
    borderBottom: '1px solid #333',
    fontSize: '0.85rem',
  },
  tableCell: {
    flex: '1',
    padding: '0 0.5rem',
    textAlign: 'left',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  tableCellCenter: {
    flex: '1',
    padding: '0 0.5rem',
    textAlign: 'center',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  headerCell: {
    flex: '1',
    padding: '0 0.5rem',
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#2196F3',
  },
};

export default function ConnectDashboard() {
  const [leadsBySource, setLeadsBySource] = useState({});
  const [selected, setSelected] = useState({});
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSources, setExpandedSources] = useState({});

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

  const toggleSourceExpand = (source) => {
    setExpandedSources(prev => ({
      ...prev,
      [source]: !prev[source]
    }));
  };

  const getStatusColor = (status) => {
    const colors = {
      'sent': { bg: '#3498db', color: '#fff' },
      'error': { bg: '#FF6347', color: '#fff' },
      'cooldown': { bg: '#e67e22', color: '#fff' },
      'no_content': { bg: '#7A8FA6', color: '#fff' },
      'default': { bg: '#2A3B4D', color: '#E0E0E0' }
    };
    return colors[status] || colors.default;
  };

  const filterLeads = (leads) => {
    if (!leads) return [];
    
    return leads.filter(lead => {
      if (searchTerm && !Object.values(lead).some(value => 
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )) {
        return false;
      }
      return true;
    });
  };

  return (
    <div style={styles.container}>
      <div style={styles.topBar}>
        <h1 style={styles.header}>Connect Dashboard</h1>
        <div style={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search leads..."
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {loading && (
        <p>Loading leads...</p>
      )}

      {!loading && Object.keys(leadsBySource).length === 0 && (
        <p>No leads found. Please go to Settings → Leads Info Settings to upload lead information.</p>
      )}

      {!loading && Object.keys(leadsBySource).length > 0 && (
        <>
          {Object.entries(leadsBySource).map(([source, leads]) => (
            <div key={source}>
              <div
                style={styles.card}
                onClick={() => toggleSourceExpand(source)}
              >
                <div style={styles.headerLine}>
                  <div style={styles.headerItem}>
                    <strong>{source}</strong>
                  </div>
                  <div style={styles.headerItem}>
                    <strong>{leads.length} Leads</strong>
                  </div>
                </div>
                <span style={{ color: '#2196F3', fontSize: '1.2rem' }}>
                    {/* {expandedSources[source] ? '▲' : '▼'} */}
                  </span>
                </div>

                {expandedSources[source] && (
                  <div style={styles.expandedContent}>
                    <div style={{ marginBottom: '1rem' }}>
                      <button 
                        style={styles.actionButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectAll(source);
                        }}
                      >
                        Select All
                      </button>
                      <button 
                        style={styles.actionButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleClearAll(source);
                        }}
                      >
                        Clear All
                      </button>
                      <button 
                        style={styles.actionButton}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSendEmails();
                        }}
                        disabled={sending}
                      >
                        {sending ? 'Sending...' : 'Send Selected Emails'}
                      </button>
                    </div>
                    
                    {/* Add the table header */}
                    <div style={styles.tableHeader}>
                      <div style={styles.headerCell}>Select</div>
                      <div style={styles.headerCell}>Name</div>
                      <div style={styles.headerCell}>Email</div>
                      <div style={styles.headerCell}>Company</div>
                      <div style={styles.headerCell}>Status</div>
                      <div style={styles.headerCell}>Email Count</div>
                    </div>
                    
                    {filterLeads(leads).map((lead) => {
                      const statusStyle = getStatusColor(lead.email_status);
                      return (
                        <div key={lead.id} style={styles.tableRow}>
                          <div style={styles.tableCell}>
                            <input
                              type="checkbox"
                              checked={selected[lead.id] || false}
                              onChange={(e) => {
                                e.stopPropagation();
                                handleCheckbox(lead.id, e.target.checked);
                              }}
                              style={{ transform: 'scale(1.2)' }}
                            />
                          </div>
                          <div style={styles.tableCell}>
                            <strong>{lead.name}</strong>
                          </div>
                          <div style={styles.tableCell}>
                            {lead.email}
                          </div>
                          <div style={styles.tableCell}>
                            {lead.company}
                          </div>
                          <div style={styles.tableCellCenter}>
                            <span style={{
                              ...styles.statusBadge,
                              backgroundColor: statusStyle.bg,
                              color: statusStyle.color
                            }}>
                              {lead.email_status || 'Not Sent'}
                            </span>
                          </div>
                          <div style={styles.tableCellCenter}>
                            {lead.email_count || 0}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
          ))}
        </>
      )}

      {result && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '1rem', 
          backgroundColor: '#1F1B24', 
          borderRadius: '8px',
          border: '1px solid #2196F3'
        }}>
          <h3>Email Send Results:</h3>
          <pre style={{ color: '#E0E0E0' }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

// export default ConnectDashboard;
