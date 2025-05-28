import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import ConnectDashboard from './components/ConnectDashboard';
import SettingsPage from './components/SettingsPage';
import HelpPage from './components/HelpPage';
import UserChat from './components/UserChat';
import AdminChatReview from './components/AdminChatReview';
import AdminLogin from './components/AdminLogin';
import LandingPage from './components/LandingPage';
import ReportPage from './components/ReportPage';
import { Box, Typography, Button } from '@mui/material';
import { Dashboard, Assessment, Settings, Help, Chat } from '@mui/icons-material';

const sidebarStyles = {
  container: {
    width: 280,
    flexShrink: 0,
    background: '#F5F7FA',  // Changed to off-white for better blending
    color: '#000000',
    padding: '24px 16px',
    borderRight: '1px solid #e0e0e0',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '4px 0 12px rgba(0,0,0,0.1)',
    position: 'sticky',
    top: 0,
    height: '100vh',
    overflowY: 'auto'
  },
  logo: {
    marginBottom: '2rem',
    textAlign: 'center',
    padding: '20px',
    background: '#FFFFFF',
    borderRadius: '12px',
    width: 'calc(100% - 32px)',
  },
  navButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    textDecoration: 'none',
    color: '#000000',
    borderRadius: '8px',
    marginBottom: '8px',
    transition: 'all 0.2s ease-in-out',
    fontWeight: 500
  },
  navButtonActive: {
    background: '#2196F3',
    color: '#FFFFFF',
    fontWeight: 600
  },
  navButtonHover: {
    background: '#E3F2FD',
    color: '#2196F3'
  }
}

function NavButton({ to, icon: Icon, children, isActive }) {
  const [isHovered, setIsHovered] = useState(false);
  
  const buttonStyle = {
    ...sidebarStyles.navButton,
    ...(isActive ? sidebarStyles.navButtonActive : {}),
    ...(isHovered && !isActive ? sidebarStyles.navButtonHover : {})
  };

  return (
    <Link 
      to={to} 
      style={buttonStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Icon sx={{ fontSize: '20px' }} />
      <Typography variant="body1" sx={{ fontWeight: 'inherit' }}>{children}</Typography>
    </Link>
  );
}

function Sidebar() {
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';
  
  if (isUserChat) {
    return null;
  }

  return (
    <Box sx={sidebarStyles.container}>
      <Box sx={sidebarStyles.logo}>
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img 
            src="/images/logo_transparent.png" 
            alt="Product Logo" 
            style={{ 
              width: '200px',  // Increased from 120px
              height: 'auto',  // Changed to auto to maintain aspect ratio
              objectFit: 'contain',
              maxWidth: '100%'
            }} 
          />
        </Link>
      </Box>
      <nav style={{ flex: 1 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <NavButton 
            to="/connect" 
            icon={Dashboard} 
            isActive={location.pathname === '/connect'}
          >
            Connect
          </NavButton>
          <NavButton 
            to="/report" 
            icon={Assessment} 
            isActive={location.pathname === '/report'}
          >
            Report
          </NavButton>
          <NavButton 
            to="/settings" 
            icon={Settings} 
            isActive={location.pathname === '/settings'}
          >
            Settings
          </NavButton>
          <NavButton 
            to="/help" 
            icon={Help} 
            isActive={location.pathname === '/help'}
          >
            Help
          </NavButton>
        </Box>
      </nav>
      <Box sx={{ 
        marginTop: 'auto', 
        padding: '20px 0', 
        textAlign: 'center'
      }}>
        <img 
          src="/images/caze_labs_logo.png" 
          alt="Caze Labs Logo" 
          style={{ 
            height: '40px', 
            opacity: 0.8 
          }} 
        />
      </Box>
    </Box>
  );
}

function App() {
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem('admin_api_key'));
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh', 
      background: '#121212',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>
      <Box sx={{ display: 'flex', flexGrow: 1 }}>
        <Sidebar />
        
        <Box component="main" sx={{ 
          flexGrow: 1, 
          background: '#121212',
          overflowY: 'auto',
          minHeight: '100vh',
          // Remove padding for UserChat to use full screen
          padding: isUserChat ? 0 : undefined
        }}>
          <Routes>
            <Route path="/connect" element={<ConnectDashboard />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/help" element={<HelpPage />} />
            <Route path="/chat" element={<UserChat />} />
            <Route path="/connect/chat-review" element={
              isAdmin ? <AdminChatReview /> : <AdminLogin onLogin={() => setIsAdmin(true)} />
            } />
            <Route path="/" element={<LandingPage />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  );
}

function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWrapper;
