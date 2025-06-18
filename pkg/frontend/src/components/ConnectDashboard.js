import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Settings } from "@mui/icons-material";

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans‑serif",
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
    fontWeight: 700,
    textAlign: "center",
    marginBottom: "1rem",
  },
  description: {
    color: "#B0B0B0",
    fontSize: "1.1rem",
    textAlign: "center",
    marginBottom: "1.5rem",
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
    display: "grid",
    gridTemplateColumns: "1fr 100px",
    alignItems: "center",
    fontWeight: 700,
    color: "#7A8FA6",
    fontSize: "1rem",
    gap: "1rem",
    width: "100%",
  },
  headerTitle: {
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  headerCount: {
    whiteSpace: "nowrap",
    justifySelf: "end",
  },
  expandedContent: {
    marginTop: "0.6rem",
    borderTop: "1px solid #444",
    paddingTop: "0.6rem",
    fontSize: "0.85rem",
    color: "#CCCCCC",
    lineHeight: 1.3,
  },
  actionButton: {
    backgroundColor: "#2196F3",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "20px",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "0.9rem",
    margin: "0.5rem 0.5rem 0.5rem 0",
    transition: "all 0.3s ease",
  },
  statusBadge: {
    padding: "0.25rem 0.8rem",
    borderRadius: "15px",
    fontSize: "0.85rem",
    fontWeight: 600,
    whiteSpace: "nowrap",
  },
  tableHeader: {
    display: "flex",
    alignItems: "center",
    padding: "0.75rem 0",
    borderBottom: "2px solid #2196F3",
    marginBottom: "0.5rem",
    fontWeight: "bold",
    color: "#2196F3",
    fontSize: "0.9rem",
  },
  tableRow: {
    display: "flex",
    alignItems: "center",
    padding: "0.5rem 0",
    borderBottom: "1px solid #333",
    fontSize: "0.85rem",
  },
  tableCell: {
    flex: 1,
    padding: "0 0.5rem",
    textAlign: "left",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  tableCellCenter: {
    flex: 1,
    padding: "0 0.5rem",
    textAlign: "center",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  headerCell: {
    flex: 1,
    padding: "0 0.5rem",
    textAlign: "center",
    fontWeight: "bold",
    color: "#2196F3",
  },
  sendButton: {
    backgroundColor: "#2196F3",
    border: "none",
    padding: "0.7rem 1.2rem",
    borderRadius: "20px",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "1rem",
    margin: "1rem 0",
    transition: "all 0.3s ease",
    width: "100%",
    maxWidth: "300px",
  },
  successMessage: {
    backgroundColor: '#4caf504d',
    color: '#4caf50',
    padding: '0.8rem',
    borderRadius: '8px',
    marginBottom: '1rem',
    border: '1px solid #4caf50',
    width: "100%",
    maxWidth: "600px",
    textAlign: "center",
  },
};

const getStatusColorByCount = (lead) => {
  if ((lead.email_count || 0) > 0)
    return { bg: "#4CAF50", color: "#fff" }; // Green
  return { bg: "#F44336", color: "#fff" }; // Red
};

const getStatusText = (lead) => {
  if ((lead.email_count || 0) > 0) return "Email Sent";
  return "Email Not Sent";
};

export default function ConnectDashboard() {
  const [leadsBySource, setLeadsBySource] = useState({});
  const [selected, setSelected] = useState({});
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedSources, setExpandedSources] = useState({});
  const [searchResults, setSearchResults] = useState([]);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    fetch("/api/leads")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.text().then(text => {
          try {
            const data = JSON.parse(text);
            return data || {}; // Ensure we always return an object
          } catch (e) {
            console.error('Failed to parse response:', text);
            throw new Error('Invalid JSON response from server');
          }
        });
      })
      .then((data) => {
        setLeadsBySource(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load leads:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Auto-dismiss success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Check if leads are present
  const hasLeads = Object.keys(leadsBySource).length > 0 &&
    Object.values(leadsBySource).some(arr => arr && arr.length > 0);

  const searchableFields = ["name", "email", "company", "phone", "position"];

  const searchMatch = (lead, term) => {
    if (!term) return false;
    const searchTerms = term.toLowerCase().split(' ');
    return searchTerms.every(searchTerm =>
      searchableFields.some(
        field => lead[field] && String(lead[field]).toLowerCase().includes(searchTerm)
      )
    );
  };

  useEffect(() => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    const results = Object.entries(leadsBySource).flatMap(([source, leads]) =>
      leads
        .filter(lead => searchMatch(lead, searchTerm.trim()))
        .map(lead => ({ ...lead, source }))
    );
    setSearchResults(results);
  }, [leadsBySource, searchTerm]);

  const toggleSourceExpand = (source) => {
    setExpandedSources(prev => ({
      ...prev,
      [source]: !prev[source]
    }));
  };

  const handleSelectAll = (source) => {
    const newSelected = { ...selected };
    const relevantLeads = searchTerm.trim()
      ? searchResults.filter(lead => lead.source === source)
      : leadsBySource[source] || [];

    relevantLeads.forEach((lead) => {
      newSelected[lead.id] = true;
    });
    setSelected(newSelected);
  };

  const handleClearAll = (source) => {
    const newSelected = { ...selected };
    const relevantLeads = searchTerm.trim()
      ? searchResults.filter(lead => lead.source === source)
      : leadsBySource[source] || [];

    relevantLeads.forEach((lead) => {
      newSelected[lead.id] = false;
    });
    setSelected(newSelected);
  };

  const handleCheckbox = (leadId, checked) => {
    setSelected({ ...selected, [leadId]: checked });
  };

  // NEW: Check if any lead is selected
  const anySelected = Object.values(selected).some(Boolean);

  // Helper to map id to name for result message
  const idToName = {};
  Object.entries(leadsBySource).forEach(([source, leads]) => {
    leads.forEach((lead) => {
      idToName[lead.id] = lead.name;
    });
  });
  if (searchResults.length > 0) {
    searchResults.forEach((lead) => {
      idToName[lead.id] = lead.name;
    });
  }

  // NEW: Send Email button handler
  const handleSendEmails = async () => {
    try {
      setSending(true);
      setResult(null);
      setError(null);
      setSuccessMessage(null);
      
      const leadIds = Object.keys(selected).filter((id) => selected[id]);

      const res = await fetch("/api/send_emails", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lead_ids: leadIds }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        console.error('Failed to parse response:', text);
        throw new Error('Invalid JSON response from server');
      }

      setResult(data);
      setSelected({}); // Clear selections after successful send
      setSuccessMessage("Emails sent successfully!");
    } catch (err) {
      console.error('Failed to send emails:', err);
      setError(err.message || 'Failed to send emails');
    } finally {
      setSending(false);
    }
  };

  // Helper: Check if leads are present
  const leadsPresent = Object.keys(leadsBySource || {}).length > 0 &&
    Object.values(leadsBySource || {}).some(arr => Array.isArray(arr) && arr.length > 0);

  return (
    <div style={styles.container}>
      <div style={styles.topBar}>
        <h1 style={styles.header}>Connect Dashboard</h1>
        <p style={{color: '#7A8FA6', marginBottom: '2rem', textAlign: 'center', maxWidth: '800px'}}>
          Manage and communicate with your leads efficiently. Select leads to send automated emails, track response status, and manage engagement all in one place.
        </p>
      </div>

      {successMessage && (
        <div style={{
          margin: '1rem',
          padding: '1rem',
          backgroundColor: '#4caf501a',
          border: '1px solid #4CAF50',
          borderRadius: '8px',
          color: '#4CAF50',
          marginBottom: '1rem'
        }}>
          {successMessage}
        </div>
      )}

      {error && (
        <div style={{
          margin: '1rem',
          padding: '1rem',
          backgroundColor: '#ff00001a',
          border: '1px solid #ff0000',
          borderRadius: '8px',
          color: '#ff0000',
          marginBottom: '1rem'
        }}>
          Error: {error}
        </div>
      )}

      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <button
          style={{
            ...styles.actionButton,
            opacity: Object.values(selected).some(Boolean) && !sending ? 1 : 0.5,
            pointerEvents: Object.values(selected).some(Boolean) && !sending ? "auto" : "none",
          }}
          onClick={handleSendEmails}
          disabled={!Object.values(selected).some(Boolean) || sending}
        >
          {sending ? "Sending..." : "Send Emails to Selected"}
        </button>

        <div style={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search by name, company, email..."
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Show loading state */}
      {loading && (
        <div style={{textAlign: 'center', padding: '2rem'}}>
          <p>Loading leads...</p>
        </div>
      )}

      {/* Show search results if there's a search term */}
      {!loading && !error && searchTerm.trim() && Array.isArray(searchResults) && (
        <div>
          <h2 style={{ color: '#7A8FA6', marginBottom: '1rem' }}>
            Search Results ({searchResults.length})
          </h2>
          {searchResults.map((lead) => (
            <div key={lead.id || Math.random()} style={styles.card}>
              <div style={{ ...styles.headerLine, marginBottom: '0.5rem' }}>
                <div style={styles.headerTitle}>{lead.name}</div>
                <div style={styles.headerCount}>{lead.source}</div>
              </div>
              <div style={{ fontSize: '0.9rem', color: '#CCCCCC' }}>
                <div>Email: {lead.email}</div>
                <div>Company: {lead.company}</div>
                {lead.position && <div>Position: {lead.position}</div>}
                {lead.phone && <div>Phone: {lead.phone}</div>}
              </div>
              <div style={{ marginTop: '1rem' }}>
                <span
                  style={{
                    ...styles.statusBadge,
                    backgroundColor: getStatusColorByCount(lead).bg,
                    color: getStatusColorByCount(lead).color,
                  }}
                >
                  {getStatusText(lead)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Show original source-based view when not searching */}
      {!loading && !error && !searchTerm.trim() && leadsPresent && (
        <>
          {Object.entries(leadsBySource || {}).map(([source, leads]) => (
            <div key={source}>
              <div style={styles.card} onClick={() => toggleSourceExpand(source)}>
                <div style={styles.headerLine}>
                  <div style={styles.headerTitle}>{source}</div>
                  <div style={styles.headerCount}>{leads.length} Leads</div>
                </div>
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
                  </div>

                  {/* table header */}
                  <div style={styles.tableHeader}>
                    <div style={styles.headerCell}>Select</div>
                    <div style={styles.headerCell}>Name</div>
                    <div style={styles.headerCell}>Email</div>
                    <div style={styles.headerCell}>Company</div>
                    <div style={styles.headerCell}>Status</div>
                    <div style={styles.headerCell}>Email Count</div>
                  </div>

                  {/* rows */}
                  {leads.map((lead) => (
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
                      <div style={styles.tableCell}><strong>{lead.name}</strong></div>
                      <div style={styles.tableCell}>{lead.email}</div>
                      <div style={styles.tableCell}>{lead.company}</div>
                      <div style={styles.tableCellCenter}>
                        <span
                          style={{
                            ...styles.statusBadge,
                            backgroundColor: getStatusColorByCount(lead).bg,
                            color: getStatusColorByCount(lead).color,
                          }}
                        >
                          {getStatusText(lead)}
                        </span>
                      </div>
                      <div style={styles.tableCellCenter}>{lead.email_count || 0}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </>
      )}

      {/* NEW: Success Message */}
      {result && !sending && (
        <div
          style={{
            marginTop: '1rem',
            padding: '1rem',
            backgroundColor: '#1F1B24',
            borderRadius: '8px',
            border: '1px solid #2196F3',
            color: '#E0E0E0'
          }}
        >
          {result.error ? (
            <p style={{color: '#ff0000'}}>{result.error}</p>
          ) : (
            <>
              <h3>Emails Sent!</h3>
              <ul>
                {result.results?.map(r => (
                  <li key={r.id}>
                    {r.id}: <b style={{ color: r.status === "sent" ? "#4CAF50" : "#F44336" }}>
                      {r.status === "sent" ? "Sent" : "Not Sent"}
                    </b>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      {/* Show no leads message */}
      {!loading && !error && !leadsPresent && (
        <div style={{
          margin: "2rem auto",
          padding: "2rem",
          textAlign: "center",
          backgroundColor: "#1F1B24",
          borderRadius: "12px",
          maxWidth: "600px"
        }}>
          <p style={{marginBottom: "1rem", color: "#CCCCCC"}}>No leads data available. Add leads in the Settings page.</p>
          <Link to="/settings" style={{
            color: "#1E88E5",
            textDecoration: "none",
            fontWeight: "600"
          }}>Go to Settings</Link>
        </div>
      )}
    </div>
  );
}
