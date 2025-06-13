import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

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
filterContainer: {
  display: "flex",
  gap: "0.8rem",
  marginBottom: "1.5rem",
  flexWrap: "wrap",
},
filterButton: {
  padding: "0.5rem 1.2rem",
  border: "none",
  borderRadius: "25px",
  backgroundColor: "#2A3B4D",
  color: "#E0E0E0",
  cursor: "pointer",
  fontWeight: "600",
  fontSize: "0.9rem",
  transition: "background-color 0.3s ease",
},
filterButtonActive: {
  backgroundColor: "#2196F3",
  color: "#fff",
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
},
headerItem: {
  flex: "1 1 auto",
  whiteSpace: "nowrap",
  overflow: "hidden",
  textOverflow: "ellipsis",
},
linkButton: {
  backgroundColor: "#2196F3",
  border: "none",
  padding: "0.25rem 0.8rem",
  borderRadius: "15px",
  color: "white",
  fontWeight: "600",
  cursor: "pointer",
  fontSize: "0.85rem",
  textDecoration: "none",
  whiteSpace: "nowrap",
},
expandedContent: {
  marginTop: "0.6rem",
  borderTop: "1px solid #444",
  paddingTop: "0.6rem",
  fontSize: "0.85rem",
  color: "#CCCCCC",
  lineHeight: "1.3",
},
debugInfo: {
  backgroundColor: "#2A2A2A",
  padding: "1rem",
  borderRadius: "8px",
  marginBottom: "1rem",
  fontSize: "0.8rem",
  fontFamily: "monospace",
},
};

const FILTERS = ["All", "Not Responded", "Hot", "Warm", "Cold"];

export default function ReportPage() {
const [leads, setLeads] = useState([]);
const [filteredLeads, setFilteredLeads] = useState([]);
const [filter, setFilter] = useState("All");
const [expandedId, setExpandedId] = useState(null);
const [searchTerm, setSearchTerm] = useState("");
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
// Meeting modal state
const [modalOpen, setModalOpen] = useState(false);
const [modalEmailContent, setModalEmailContent] = useState("");
const [modalLeadId, setModalLeadId] = useState(null);
const [meetingLoading, setMeetingLoading] = useState(false);

// Fetch data effect
const fetchLeads = async () => {
  try {
    setLoading(true);
    setError(null);
    const res = await fetch("/api/report");
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    if (data && Array.isArray(data.leads)) {
      setLeads(data.leads);
      setFilteredLeads(data.leads);
    } else {
      setLeads([]);
      setFilteredLeads([]);
      setError("API response did not contain leads array");
    }
  } catch (error) {
    setError(`Failed to fetch leads: ${error.message}`);
    setLeads([]);
    setFilteredLeads([]);
  } finally {
    setLoading(false);
  }
};

useEffect(() => { fetchLeads(); }, []);

// Filtering/search effect
useEffect(() => {
  let updated = [...leads];
  if (filter !== "All") {
    updated = updated.filter((lead) => {
      const status = lead["Status (Hot/Warm/Cold/Not Responded)"] || "";
      return status.toLowerCase().trim() === filter.toLowerCase().trim();
    });
  }
  if (searchTerm.trim() !== "") {
    const term = searchTerm.toLowerCase().trim();
    updated = updated.filter((lead) => {
      const nameMatch = (lead.Name || "").toLowerCase().includes(term);
      const emailMatch = (lead.Email || "").toLowerCase().includes(term);
      const companyMatch = (lead.Company || "").toLowerCase().includes(term);
      return nameMatch || emailMatch || companyMatch;
    });
  }
  setFilteredLeads(updated);
  setExpandedId(null);
}, [filter, searchTerm, leads]);

const toggleExpand = (id) => {
  setExpandedId(expandedId === id ? null : id);
};

// --- Meeting Scheduling Logic ---
// Helper to get meeting fields from lead (handles different casing/keys)
const getMeetingFields = (lead) => {
  return {
    pendingMeetingEmail: lead["Pending Meeting Email"] || lead.pending_meeting_email || "",
    meetingEmailSent: lead["Meeting Email Sent"] || lead.meeting_email_sent || "",
    pendingMeetingInfo: lead["Pending Meeting Info"] || lead.pending_meeting_info || "",
    status: lead["Status (Hot/Warm/Cold/Not Responded)"] || lead.status || "",
    chatSummary: lead["Chat Summary"] || lead.chat_summary || "",
  };
};

// Generate meeting proposal for Warm/Cold
const handleGenerateMeeting = async (leadId) => {
  setMeetingLoading(true);
  await fetch("/api/generate_meeting_proposal", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lead_id: leadId })
  });
  await fetchLeads();
  setMeetingLoading(false);
};

// Review meeting email (open modal)
const handleReviewEmail = async (leadId) => {
  setMeetingLoading(true);
  const res = await fetch("/api/review_meeting_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lead_id: leadId })
  });
  const data = await res.json();
  setModalEmailContent(data.email_content || "");
  setModalLeadId(leadId);
  setModalOpen(true);
  setMeetingLoading(false);
};

// Send meeting email
const handleSendEmail = async () => {
  if (!modalLeadId) return;
  setMeetingLoading(true);
  await fetch("/api/send_meeting_email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lead_id: modalLeadId })
  });
  setModalOpen(false);
  setModalLeadId(null);
  setModalEmailContent("");
  await fetchLeads();
  setMeetingLoading(false);
};

// --- UI ---
if (loading) {
  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Loading...</h1>
    </div>
  );
}

return (
  <div style={styles.container}>
    <div style={styles.topBar}>
      <h1 style={styles.header}>Leads Report</h1>
      <p style={{color: '#7A8FA6', marginBottom: '2rem', textAlign: 'center', maxWidth: '800px', margin: '0 auto 2rem'}}>
        View and analyze your leads' engagement status. Filter by response status, search for specific leads, and access detailed interaction history.
      </p>
    </div>

    {/* Show guidance message if no leads */}
    {!loading && leads.length === 0 && (
      <div style={{
        margin: "2rem auto",
        padding: "2rem",
        textAlign: "center",
        backgroundColor: "#1F1B24",
        borderRadius: "12px",
        maxWidth: "600px"
      }}>
        <p style={{marginBottom: "1rem", color: "#CCCCCC"}}>No leads data available. First, add leads in the Settings page.</p>
        <Link to="/settings" style={{
          color: "#1E88E5",
          textDecoration: "none",
          fontWeight: "600",
          marginRight: "1rem",
        }}>Go to Settings</Link>
      </div>
    )}

    {/* Show search and filters only if we have leads */}
    {leads.length > 0 && (
      <>
        <div style={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search by name, email or company"
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={styles.filterContainer}>
          {FILTERS.map((f) => (
            <button
              key={f}
              style={{
                ...styles.filterButton,
                ...(filter === f ? styles.filterButtonActive : {}),
              }}
              onClick={() => setFilter(f)}
            >
              {f} ({leads.filter(lead => f === "All" || (lead["Status (Hot/Warm/Cold/Not Responded)"] || "").toLowerCase().trim() === f.toLowerCase().trim()).length})
            </button>
          ))}
        </div>

        {/* Show no results message for filters/search */}
        {filteredLeads.length === 0 && (
          <div style={{
            margin: "2rem auto",
            padding: "2rem",
            textAlign: "center",
            backgroundColor: "#1F1B24",
            borderRadius: "12px",
            maxWidth: "600px"
          }}>
            <p style={{marginBottom: "1rem", color: "#CCCCCC"}}>
              No leads found matching your criteria. Try adjusting your search or filter.
            </p>
            <Link to="/connect" style={{
              color: "#1E88E5",
              textDecoration: "none",
              fontWeight: "600"
            }}>View All Leads</Link>
          </div>
        )}

        {/* Show leads list */}
        {filteredLeads.map((lead, index) => {
          const {
            pendingMeetingEmail,
            meetingEmailSent,
            status,
            chatSummary
          } = getMeetingFields(lead);
          return (
            <div
              key={lead.ID || index}
              style={styles.card}
              onClick={() => toggleExpand(lead.ID || index)}
            >
              <div style={styles.headerLine}>
                <div style={styles.headerItem} title={lead.Name || 'No Name'}>
                  <strong>Name:</strong> {lead.Name || 'No Name'}
                </div>
                <div style={styles.headerItem} title={lead.Company || 'No Company'}>
                  <strong>Company:</strong> {lead.Company || 'No Company'}
                </div>
                {lead["Private Link"] && (
                  <a
                    href={lead["Private Link"]}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.linkButton}
                    onClick={(e) => e.stopPropagation()}
                  >
                    Chat Link
                  </a>
                )}
              </div>

              {expandedId === (lead.ID || index) && (
                <div style={styles.expandedContent}>
                  <div><strong>Description:</strong> {lead.Description || "-"}</div>
                  <div><strong>Email:</strong> {lead.Email || "-"}</div>
                  <div><strong>Connected:</strong> {lead.Connected ? "Yes" : "No"}</div>
                  <div><strong>Sent Date:</strong> {lead["Sent Date"] || "-"}</div>
                  <div><strong>Source:</strong> {lead.source || "-"}</div>
                  <div>
                    <strong>Chat Summary:</strong>{" "}
                    {chatSummary ? chatSummary : "-"}
                  </div>
                  <div><strong>Status:</strong> {status || "-"}</div>

                  {/* --- MEETING SCHEDULER UI --- */}
                  {chatSummary && (
                    <div style={{ marginTop: '1rem' }}>
                      {/* Hot lead logic */}
                      {status === 'Hot' && (
                        <>
                          {meetingEmailSent === 'Yes' ? (
                            <div style={{ color: '#4caf50', fontWeight: 600 }}>Meeting Sent</div>
                          ) : pendingMeetingEmail ? (
                            <button
                              style={{ ...styles.linkButton, backgroundColor: '#ff9800', color: '#fff', marginRight: 8 }}
                              onClick={e => { e.stopPropagation(); handleReviewEmail(lead.ID); }}
                              disabled={meetingLoading}
                            >
                              Review Email
                            </button>
                          ) : (
                            <span style={{ color: '#aaa' }}>Generating proposal...</span>
                          )}
                        </>
                      )}
                      {/* Warm/Cold logic */}
                      {(status === 'Warm' || status === 'Cold') && (
                        <>
                          {!pendingMeetingEmail ? (
                            <button
                              style={{ ...styles.linkButton, backgroundColor: '#2196F3', color: '#fff', marginRight: 8 }}
                              onClick={e => { e.stopPropagation(); handleGenerateMeeting(lead.ID); }}
                              disabled={meetingLoading}
                            >
                              {meetingLoading ? 'Generating...' : 'Generate Meeting Link'}
                            </button>
                          ) : meetingEmailSent === 'Yes' ? (
                            <div style={{ color: '#4caf50', fontWeight: 600 }}>Meeting Sent</div>
                          ) : (
                            <button
                              style={{ ...styles.linkButton, backgroundColor: '#ff9800', color: '#fff', marginRight: 8 }}
                              onClick={e => { e.stopPropagation(); handleReviewEmail(lead.ID); }}
                              disabled={meetingLoading}
                            >
                              Review Email
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* --- MODAL FOR EMAIL REVIEW/SEND --- */}
        {modalOpen && (
          <div style={{
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <div style={{ background: '#232323', padding: 32, borderRadius: 12, minWidth: 350, maxWidth: 600 }}>
              <h2 style={{ color: '#ff9800', marginBottom: 16 }}>Review Meeting Email</h2>
              <pre style={{ background: '#181818', color: '#fff', padding: 16, borderRadius: 8, maxHeight: 300, overflow: 'auto' }}>{modalEmailContent}</pre>
              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <button
                  style={{ ...styles.linkButton, backgroundColor: '#2196F3', color: '#fff' }}
                  onClick={handleSendEmail}
                  disabled={meetingLoading}
                >
                  {meetingLoading ? 'Sending...' : 'Send'}
                </button>
                <button
                  style={{ ...styles.linkButton, backgroundColor: '#444', color: '#fff' }}
                  onClick={() => setModalOpen(false)}
                  disabled={meetingLoading}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    )}
  </div>
);
}