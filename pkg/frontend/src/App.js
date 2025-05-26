import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ConnectDashboard from './components/ConnectDashboard';
import SettingsPage from './components/SettingsPage';
import UserChat from './components/UserChat';
import AdminChatReview from './components/AdminChatReview';
import AdminLogin from './components/AdminLogin';
import LandingPage from './components/LandingPage';
import ReportPage from './components/ReportPage';
import { Box, Typography } from '@mui/material';

function App() {
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem('admin_api_key'));

  return (
    <Router>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#1a2027' }}>
        <Box sx={{ display: 'flex', flexGrow: 1 }}>
          <Box sx={{ width: 240, flexShrink: 0, bgcolor: '#2d3748', color: '#e2e8f0', padding: '20px', borderRight: '1px solid #4a5568', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ marginBottom: 4 }}>
              <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                <img src="/images/logo_transparent.png" alt="Product Logo" style={{ width: '100%', height: 'auto' }} />
              </Link>
            </Box>
            <nav>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, padding: '20px 0' }}>
                <Link to="/connect" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Typography variant="body1" sx={{ '&:hover': { color: '#BE232F' } }}>Connect</Typography>
                </Link>
                <Link to="/report" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Typography variant="body1" sx={{ '&:hover': { color: '#BE232F' } }}>Report</Typography>
                </Link>
                <Link to="/settings" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Typography variant="body1" sx={{ '&:hover': { color: '#BE232F' } }}>Settings</Typography>
                </Link>
                <Link to="/help" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Typography variant="body1" sx={{ '&:hover': { color: '#BE232F' } }}>Help</Typography>
                </Link>
              </Box>
            </nav>
          </Box>

          <Box component="main" sx={{ flexGrow: 1, padding: 3, overflowY: 'auto' }}>
            <Routes>
              <Route path="/connect" element={<ConnectDashboard />} />
              <Route path="/report" element={<ReportPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/chat" element={<UserChat />} />
              <Route path="/connect/chat-review" element={
                isAdmin ? <AdminChatReview /> : <AdminLogin onLogin={() => setIsAdmin(true)} />
              } />
              <Route path="/" element={<LandingPage />} />
            </Routes>
          </Box>
        </Box>
        <Box component="footer" sx={{ bgcolor: '#1a2027', color: '#e2e8f0', padding: 2, textAlign: 'center' }}>
          <img src="/images/caze_labs_logo.png" alt="Caze Labs Logo" style={{ height: 30 }} />
        </Box>
      </Box>
    </Router>
  );
}

export default App; 