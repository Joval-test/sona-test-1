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
import { Box, Typography, IconButton } from '@mui/material';
import { Dashboard, Assessment, Settings, Help, Chat, Menu } from '@mui/icons-material';

const sidebarStyles = {
  container: {
    width: 280,
    flexShrink: 0,
    background: '#F5F7FA',
    color: '#000000',
    padding: '24px 16px',
    borderRight: '1px solid #e0e0e0',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '4px 0 12px rgba(0,0,0,0.1)',
    position: 'fixed',
    height: '100vh',
    overflowY: 'auto',
    transition: 'transform 0.3s ease-in-out',
    zIndex: 1000,
  },  containerClosed: {
    transform: 'translateX(-100%)',
    visibility: 'hidden',
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
  },  mainContentShift: {
    marginLeft: '312px',  // 280px + padding
    transition: 'all 0.3s ease-in-out',
    width: 'calc(100% - 312px)',
    padding: '24px',
  },
  mainContentFull: {
    marginLeft: '0',
    width: '100%',
    padding: '24px',
    transition: 'all 0.3s ease-in-out',
  },  header: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '64px',
    background: '#1E1E1E',
    display: 'flex',
    alignItems: 'center',
    padding: '0 20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
    zIndex: 999,
  },
  headerLogo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginLeft: '12px',
  },
  headerImage: {
    height: '32px',
    width: 'auto',
    padding: '4px',
    background: '#FFFFFF',
    borderRadius: '8px',
  },
  headerTitle: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#FFFFFF',  
  },
};

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

function Sidebar({ isOpen, onToggle }) {
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';
  
  if (isUserChat) {
    return null;
  }

  return (
    <Box sx={{
      ...sidebarStyles.container,
      ...(isOpen ? {} : sidebarStyles.containerClosed),
    }}>
      <Box sx={sidebarStyles.logo}>
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img 
            src="/images/logo_transparent.png" 
            alt="Product Logo" 
            style={{ 
              width: '200px',
              height: 'auto',
              objectFit: 'contain',
              maxWidth: '100%'
            }} 
          />
        </Link>
      </Box>
      <nav style={{ flex: 1 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <NavButton to="/connect" icon={Dashboard} isActive={location.pathname === '/connect'}>
            Connect
          </NavButton>
          <NavButton to="/report" icon={Assessment} isActive={location.pathname === '/report'}>
            Report
          </NavButton>
          <NavButton to="/settings" icon={Settings} isActive={location.pathname === '/settings'}>
            Settings
          </NavButton>
          <NavButton to="/help" icon={Help} isActive={location.pathname === '/help'}>
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

function Header({ isOpen, onToggle }) {
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';
  
  if (isUserChat) {
    return null;
  }
  return (
    <Box sx={sidebarStyles.header}>
      <IconButton 
        onClick={onToggle}
        size="large"
        edge="start"
        aria-label="menu"
        sx={{ color: '#FFFFFF' }}  // Make hamburger icon white
      >
        <Menu />
      </IconButton>
      {!isOpen && (
        <Box sx={sidebarStyles.headerLogo}>
          <img 
            src="/images/icon.png" 
            alt="Caze Icon" 
            style={sidebarStyles.headerImage}
          />
          <Typography sx={sidebarStyles.headerTitle}>
            Caze BizCon AI
          </Typography>
        </Box>
      )}
    </Box>
  );
}

function App() {
  const [isAdmin, setIsAdmin] = useState(!!localStorage.getItem('admin_api_key'));
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh', 
      background: '#121212',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>
      <Header isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <Box sx={{ display: 'flex', flexGrow: 1, marginTop: '64px' }}>
        <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
        
        <Box component="main" sx={{ 
          flexGrow: 1, 
          background: '#121212',
          overflowY: 'auto',
          minHeight: 'calc(100vh - 64px)',
          padding: isUserChat ? 0 : undefined,
          ...(isSidebarOpen ? sidebarStyles.mainContentShift : sidebarStyles.mainContentFull),
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
