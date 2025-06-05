import React, { useState, useEffect } from 'react';

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

// // Fetch data effect
useEffect(() => {
  async function fetchData() {
    try {
      setLoading(true);
      setError(null);
      
      // For testing purposes, use mock data
      // Replace this with your actual API call
      const useMockData = false; // Set to false when API is ready
      
      if (useMockData) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        const data = mockData;
        
        if (data && Array.isArray(data.leads)) {
          setLeads(data.leads); 
          setFilteredLeads(data.leads);
        } else {
          setLeads([]);
          setFilteredLeads([]);
          setError("Mock data structure is invalid");
        }
      } else {        const res = await fetch("/api/report");
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        if (data && Array.isArray(data.leads)) {
          setLeads(data.leads); 
          setFilteredLeads(data.leads);
        } else {
          setLeads([]);
          setFilteredLeads([]);
          setError("API response did not contain leads array");
        }
      }
    } catch (error) {
      console.error("Failed to fetch leads", error);
      setError(`Failed to fetch leads: ${error.message}`);
      setLeads([]);
      setFilteredLeads([]);
    } finally {
      setLoading(false);
    }
  }
  fetchData();
}, []);

// Filtering/search effect
useEffect(() => {
  let updated = [...leads]; // Create a copy
  
  console.log("Filtering leads. Current filter:", filter, "Search term:", searchTerm);
  console.log("Original leads count:", leads.length);

  if (filter !== "All") {
    updated = updated.filter((lead) => {
      const status = lead["Status (Hot/Warm/Cold/Not Responded)"] || "";
      const match = status.toLowerCase().trim() === filter.toLowerCase().trim();
      console.log(`Lead ${lead.Name}: status="${status}", filter="${filter}", match=${match}`);
      return match;
    });
    console.log("After filter:", updated.length, "leads");
  }

  if (searchTerm.trim() !== "") {
    const term = searchTerm.toLowerCase().trim();
    updated = updated.filter((lead) => {
      const nameMatch = (lead.Name || "").toLowerCase().includes(term);
      const emailMatch = (lead.Email || "").toLowerCase().includes(term);
      const companyMatch = (lead.Company || "").toLowerCase().includes(term);
      const match = nameMatch || emailMatch || companyMatch;
      console.log(`Search "${term}" in lead ${lead.Name}: name=${nameMatch}, email=${emailMatch}, company=${companyMatch}, match=${match}`);
      return match;
    });
    console.log("After search:", updated.length, "leads");
  }

  setFilteredLeads(updated);
  setExpandedId(null);
}, [filter, searchTerm, leads]);

const toggleExpand = (id) => {
  setExpandedId(expandedId === id ? null : id);
};

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
      <div style={styles.searchContainer}>
        <input
          type="text"
          placeholder="Search by name, email or company"
          style={styles.searchInput}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
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

    {error && (
      <div style={{color: '#ff6b6b', marginBottom: '1rem'}}>
        Error: {error}
      </div>
    )}

    {filteredLeads.length === 0 && !loading && (
      <p>
        {leads.length === 0 
          ? "No leads available" 
          : `No leads found for filter "${filter}" ${searchTerm ? `and search "${searchTerm}"` : ''}`
        }
      </p>
    )}

    {filteredLeads.map((lead, index) => {
      console.log(`Rendering lead ${index}:`, lead);
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
                {(lead["Chat Summary"] !== undefined && !isNaN(lead["Chat Summary"])) ? 
                  lead["Chat Summary"] : "-"}
              </div>
              <div><strong>Status:</strong> {lead["Status (Hot/Warm/Cold/Not Responded)"] || "-"}</div>
            </div>
          )}
        </div>
      );
    })}
  </div>
);
}