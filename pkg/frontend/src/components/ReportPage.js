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
    backgroundColor: "#2196F3", // Changed from #FF6347 to blue
    color: "#fff",
  },
  card: {
    backgroundColor: "#1F1B24",
    borderRadius: "12px",
    padding: "0.8rem 1rem",
    boxShadow: "0 3px 8px rgba(33, 150, 243, 0.3)", // Changed from rgba(255, 99, 71, 0.3) to blue
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
    backgroundColor: "#2196F3", // Changed from #FF6347 to blue
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
};

const FILTERS = ["All", "Not Responded", "Hot", "Warm", "Cold"];

export default function ReportPage() {
  const [leads, setLeads] = useState([]);
  const [filteredLeads, setFilteredLeads] = useState([]);
  const [filter, setFilter] = useState("All");
  const [expandedId, setExpandedId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch("http://localhost:5000/api/report");
        const data = await res.json();
        if (data && Array.isArray(data.leads)) {
          setLeads(data.leads);
          setFilteredLeads(data.leads);
        } else {
          setLeads([]);
          setFilteredLeads([]);
        }
      } catch (error) {
        console.error("Failed to fetch leads", error);
        setLeads([]);
        setFilteredLeads([]);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    let updated = leads;

    if (filter !== "All") {
      updated = updated.filter(
        (lead) =>
          (lead["Status (Hot/Warm/Cold/Not Responded)"] || "")
            .toLowerCase()
            === filter.toLowerCase()
      );
    }

    if (searchTerm.trim() !== "") {
      updated = updated.filter((lead) => {
        const term = searchTerm.toLowerCase();
        return (
          (lead.Name || "").toLowerCase().includes(term) ||
          (lead.Email || "").toLowerCase().includes(term) ||
          (lead.Company || "").toLowerCase().includes(term)
        );
      });
    }

    setFilteredLeads(updated);
    setExpandedId(null);
  }, [filter, searchTerm, leads]);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

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
            {f}
          </button>
        ))}
      </div>

      {filteredLeads.length === 0 && (
        <p>No leads found for "{filter}"</p>
      )}

      {filteredLeads.map((lead) => (
        <div
          key={lead.ID}
          style={styles.card}
          onClick={() => toggleExpand(lead.ID)}
        >
          <div style={styles.headerLine}>
            <div style={styles.headerItem} title={lead.Name}>
              <strong>Name:</strong> {lead.Name}
            </div>
            <div style={styles.headerItem} title={lead.Company}>
              <strong>Company:</strong> {lead.Company}
            </div>
            <a
              href={lead["Private Link"]}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.linkButton}
              onClick={(e) => e.stopPropagation()}
            >
              Chat Link
            </a>
          </div>

          {expandedId === lead.ID && (
            <div style={styles.expandedContent}>
              <div><strong>Description:</strong> {lead.Description || "-"}</div>
              <div><strong>Email:</strong> {lead.Email || "-"}</div>
              <div><strong>Connected:</strong> {lead.Connected ? "Yes" : "No"}</div>
              <div><strong>Sent Date:</strong> {lead["Sent Date"] || "-"}</div>
              <div><strong>Source:</strong> {lead.source || "-"}</div>
              <div><strong>Chat Summary:</strong> {isNaN(lead["Chat Summary"]) ? lead["Chat Summary"] : "-"}</div>
              <div><strong>Status:</strong> {lead["Status (Hot/Warm/Cold/Not Responded)"] || "-"}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
