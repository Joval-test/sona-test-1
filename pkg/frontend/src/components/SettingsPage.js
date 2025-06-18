import React, { useState } from 'react';
import EmailSettings from './EmailSettings';
import AzureSettings from './AzureSettings';
import PrivateLinkSettings from './PrivateLinkSettings';
import CompanyInfoSettings from './CompanyInfoSettings';
import LeadsInfoSettings from './LeadsInfoSettings';
import { CircularProgress } from '@mui/material';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  header: {
    color: "#7A8FA6",
    fontSize: "2rem",
    fontWeight: "700",
    marginBottom: "1.5rem"
  },
  tabContainer: {
    display: "flex",
    gap: "0.8rem",
    marginBottom: "2rem",
    flexWrap: "wrap",
  },
  tabButton: {
    padding: "0.5rem 1.2rem",  // Changed to match ReportPage button padding
    border: "none",
    borderRadius: "25px",
    backgroundColor: "#2A3B4D",
    color: "#E0E0E0",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "0.9rem",  // Changed to match ReportPage button font size
    transition: "all 0.3s ease",
    boxShadow: "0 2px 8px rgba(0,0,0,0.2)"
  },
  tabButtonActive: {
    backgroundColor: "#2196F3", // Changed from #FF6347 to blue
    color: "#fff",
    boxShadow: "0 4px 12px rgba(33, 150, 243, 0.4)", // Changed from rgba(255, 99, 71, 0.4) to blue
    transform: "translateY(-2px)"
  },
  contentCard: {
    backgroundColor: "#1F1B24",
    borderRadius: "16px",
    padding: "2rem",
    boxShadow: "0 4px 20px rgba(33, 150, 243, 0.1)", // Changed from rgba(255, 99, 71, 0.1) to blue
    marginBottom: "2rem",
    border: "1px solid #2A3B4D"
  },
  clearSection: {
    backgroundColor: "#1F1B24",
    borderRadius: "16px",
    padding: "2rem",
    boxShadow: "0 4px 20px rgba(33, 150, 243, 0.1)", // Changed from rgba(190, 35, 47, 0.1) to blue
    border: "1px solid #2196F3" // Changed from #BE232F to blue
  },
  clearButton: {
    backgroundColor: "#2196F3", // Changed from #BE232F to blue
    color: "white",
    border: "none",
    padding: "0.8rem 2rem",
    borderRadius: "25px",
    fontWeight: "600",
    cursor: "pointer",
    fontSize: "0.95rem",
    transition: "all 0.3s ease",
    marginTop: "1rem"
  },
  alertMessage: {
    backgroundColor: "#304654",
    color: "#E0E0E0",
    padding: "1rem 1.5rem",
    borderRadius: "12px",
    marginBottom: "1.5rem",
    border: "1px solid #2196F3" // Changed from #FF6347 to blue
  }
};

function SettingsPage() {
  const [tab, setTab] = useState('email');
  const [message, setMessage] = useState('');
  const [clearing, setClearing] = useState(false);

  const handleClearAll = async () => {
    setClearing(true);
    setMessage('');
    const res = await fetch('/api/clear-all', { method: 'POST' });
    const data = await res.json();
    setMessage(data.message);
    setClearing(false);
  };

  const tabs = [
    { 
      id: 'email', 
      label: 'Email Settings',
      description: 'Configure your email settings for automated communications with leads.'
    },
    { 
      id: 'azure', 
      label: 'Azure Config',
      description: 'Set up your Azure OpenAI configuration for AI-powered features.'
    },
    { 
      id: 'private', 
      label: 'Private Links',
      description: 'Manage private chat links for secure conversations with leads.'
    },
    { 
      id: 'company', 
      label: 'Company Info',
      description: 'Upload and manage your company information and documents.'
    },
    { 
      id: 'leads', 
      label: 'Leads Data',
      description: 'Import and manage your leads database.'
    }
  ];

  const renderTabContent = () => {
    switch(tab) {
      case 'email': return <EmailSettings />;
      case 'azure': return <AzureSettings />;
      case 'private': return <PrivateLinkSettings />;
      case 'company': return <CompanyInfoSettings />;
      case 'leads': return <LeadsInfoSettings />;
      default: return <EmailSettings />;
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>Settings</h1>
      
      <div style={styles.tabContainer}>
        {tabs.map((tabItem) => (
          <button
            key={tabItem.id}
            style={{
              ...styles.tabButton,
              ...(tab === tabItem.id ? styles.tabButtonActive : {}),
            }}
            onClick={() => {
              setTab(tabItem.id);
              setMessage('');
            }}
          >
            {tabItem.label}
          </button>
        ))}
      </div>

      {tab && (
        <p style={{
          color: '#7A8FA6',
          margin: '1rem 0 2rem',
          fontSize: '1rem',
          textAlign: 'center',
        }}>
          {tabs.find(t => t.id === tab)?.description}
        </p>
      )}

      {message && (
        <div style={styles.alertMessage}>
          {message}
        </div>
      )}

      <div style={styles.contentCard}>
        {renderTabContent()}
      </div>

      <div style={styles.clearSection}>
        <h3 style={{ color: '#2196F3', marginBottom: '1rem', fontSize: '1.3rem', fontWeight: '600' }}>Danger Zone</h3>
        <p style={{ color: '#CCCCCC', marginBottom: '1rem', lineHeight: '1.5' }}>
          This action will permanently delete all uploaded data, configurations, and chat histories. This cannot be undone.
        </p>
        <button
          style={{
            ...styles.clearButton,
            opacity: clearing ? 0.7 : 1,
            cursor: clearing ? 'not-allowed' : 'pointer'
          }}
          onClick={handleClearAll}
          disabled={clearing}
        >
          {clearing ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CircularProgress size={16} color="inherit" />
              Clearing...
            </span>
          ) : (
            'Clear All Data'
          )}
        </button>
      </div>
    </div>
  );
}

export default SettingsPage;