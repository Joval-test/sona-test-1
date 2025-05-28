import React, { useState, useEffect } from "react";

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

  useEffect(() => {
    fetch("/api/leads")
      .then((res) => res.json())
      .then((data) => {
        setLeadsBySource(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load leads:", err);
        setLoading(false);
      });
  }, []);

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
    setSending(true);
    setResult(null);
    const leadIds = Object.keys(selected)
      .filter((id) => selected[id]);

    const res = await fetch("/api/send_emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lead_ids: leadIds }),
    });

    const data = await res.json();
    setResult(data);
    setSending(false);

    // Optionally refresh leads if backend updates email_count
    // setLoading(true);
    // fetch("/api/leads")
    //   .then((res) => res.json())
    //   .then((data) => {
    //     setLeadsBySource(data);
    //     setLoading(false);
    //   });
  };

  // Helper: Check if leads are present
  const leadsPresent = Object.keys(leadsBySource).length > 0 &&
    Object.values(leadsBySource).some(arr => arr && arr.length > 0);

  return (
    <div style={styles.container}>
      <div style={styles.topBar}>
        <h1 style={styles.header}>Connect Dashboard</h1>
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

      {/* NEW: If no leads, prompt user to go to settings */}
      {!loading && !leadsPresent && (
        <div
          style={{
            margin: "2rem auto",
            padding: "2rem",
            maxWidth: 480,
            background: "#232323",
            borderRadius: 12,
            border: "1px solid #2196F3",
            color: "#E0E0E0",
            textAlign: "center",
          }}
        >
          <h2>No leads found</h2>
          <p>
            Please go to the <b>Settings</b> page to upload your leads and company files.<br />
            Once you have uploaded, return here to manage and email your leads.
          </p>
        </div>
      )}

      {/* NEW: Global Send Email Button, right aligned */}
      {leadsPresent && (
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "1rem" }}>
          <button
            style={{
              ...styles.actionButton,
              opacity: anySelected && !sending ? 1 : 0.5,
              pointerEvents: anySelected && !sending ? "auto" : "none",
              minWidth: "120px"
            }}
            onClick={handleSendEmails}
            disabled={!anySelected || sending}
          >
            {sending ? "Sending..." : "Send Email"}
          </button>
        </div>
      )}

      {/* NEW: Loading Bar */}
      {sending && (
        <div style={{
          width: "100%",
          background: "#333",
          borderRadius: "8px",
          margin: "1rem 0",
          height: "8px",
          overflow: "hidden"
        }}>
          <div style={{
            width: "100%",
            height: "100%",
            background: "linear-gradient(90deg, #2196F3 40%, #4CAF50 100%)",
            animation: "loading-bar 1s linear infinite"
          }} />
          <style>
            {`
              @keyframes loading-bar {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
              }
            `}
          </style>
        </div>
      )}

      {loading && <p>Loading leads…</p>}

      {/* Show search results if there's a search term */}
      {!loading && leadsPresent && searchTerm.trim() && (
        <div>
          <h2 style={{ color: '#7A8FA6', marginBottom: '1rem' }}>
            Search Results ({searchResults.length})
          </h2>
          {searchResults.map((lead) => (
            <div key={lead.id} style={styles.card}>
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
      {!loading && leadsPresent && !searchTerm.trim() && Object.keys(leadsBySource).length > 0 && (
        <>
          {Object.entries(leadsBySource).map(([source, leads]) => (
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
          <h3>Emails Sent!</h3>
          <ul>
            {result.results.map(r => (
              <li key={r.id}>
                {idToName[r.id] || r.id}: <b style={{ color: r.status === "sent" ? "#4CAF50" : "#F44336" }}>
                  {r.status === "sent" ? "Sent" : "Not Sent"}
                </b>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
