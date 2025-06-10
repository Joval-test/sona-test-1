import React, { useState, useEffect } from 'react';
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
    position: 'fixed',
    top: '64px', // Start below the header
    left: 0,
    width: 280,
    height: 'calc(100vh - 64px)', // Full height minus header
    background: '#F5F7FA',
    color: '#000000',
    padding: '24px 16px',
    borderRight: '1px solid #e0e0e0',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '4px 0 12px rgba(0,0,0,0.1)',
    overflowY: 'auto',
    transition: 'transform 0.3s ease-in-out',
    zIndex: 1000,
  },
  containerClosed: {
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
    flexShrink: 0, // Prevent logo from shrinking
  },
  navButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    textDecoration: 'none',
    color: '#000000',
    borderRadius: '12px',
    marginBottom: '10px',
    background: '#F5F7FA',
    boxShadow: '0 2px 8px rgba(33, 150, 243, 0.08)',
    transition: 'all 0.2s cubic-bezier(.4,0,.2,1)',
    fontWeight: 500,
    fontSize: '0.98rem',
    border: '2px solid transparent',
    cursor: 'pointer',
    minHeight: '36px',
    flexShrink: 0, // Prevent nav buttons from shrinking
  },
  navButtonHover: {
    background: '#E3F2FD',
    boxShadow: '0 4px 16px rgba(33, 150, 243, 0.16)',
    color: '#1976D2',
    border: '2px solid #2196F3',
    transform: 'translateY(-1px) scale(1.01)',
  },
  navButtonActive: {
    background: '#2196F3',
    color: '#fff',
    boxShadow: '0 6px 24px rgba(33, 150, 243, 0.24)',
    border: '2px solid #1976D2',
    transform: 'scale(1.02)',
  },
  navSection: {
    flex: 1, // Take up available space
    display: 'flex',
    flexDirection: 'column',
    minHeight: 0, // Allow flex items to shrink below content size
  },
  bottomLogo: {
    marginTop: 'auto',
    padding: '20px 0',
    textAlign: 'center',
    background: 'transparent',
    flexShrink: 0, // Prevent bottom logo from shrinking
  },
  mainContentShift: {
    marginLeft: '280px', // Sidebar width
    transition: 'all 0.3s ease-in-out',
    width: 'calc(100% - 280px)',
    padding: '24px',
  },
  mainContentFull: {
    marginLeft: '0',
    width: '100%',
    padding: '24px',
    transition: 'all 0.3s ease-in-out',
  },
  header: {
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
    zIndex: 1001, // Higher than sidebar
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
      <Typography variant="body1" sx={{ fontWeight: 'inherit', fontSize: '0.98rem' }}>{children}</Typography>
    </Link>
  );
}

function Sidebar({ isOpen, onToggle }) {
  const location = useLocation();
  const isUserChat = location.pathname === '/chat';
  
  if (isUserChat) {
    return null;
  }

  const sidebarContainerStyle = {
    ...sidebarStyles.container,
    ...(isOpen ? {} : sidebarStyles.containerClosed)
  };

  return (
    <Box sx={sidebarContainerStyle}>
      <Box sx={sidebarStyles.logo}>
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <img 
            src="/images/logo_transparent.png" 
            alt="Product Logo" 
            style={{ 
              width: '200px',
              height: 'auto',
              objectFit: 'contain',
              maxWidth: '100%',
            }} 
          />
        </Link>
      </Box>
      
      <nav style={sidebarStyles.navSection}>
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
      
      <Box sx={sidebarStyles.bottomLogo}>
        <img 
          src="/images/caze_labs_logo.png" 
          alt="Caze Labs Logo" 
          style={{ 
            height: '40px',
            width: 'auto',
            opacity: 0.8,
            objectFit: 'contain',
            display: 'inline-block',
            margin: 0,
            padding: 0,
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
        sx={{ color: '#FFFFFF' }}
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

  // Collapse sidebar on landing page, expand on other pages
  useEffect(() => {
    if (location.pathname === '/') {
      setIsSidebarOpen(false);
    } else {
      setIsSidebarOpen(true);
    }
  }, [location.pathname]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Calculate main content margin based on sidebar state
  const getMainContentStyle = () => {
    if (isUserChat) {
      return {
        marginLeft: 0,
        width: '100%',
        padding: 0,
      };
    }
    
    return {
      marginLeft: isSidebarOpen ? '280px' : '0px',
      width: isSidebarOpen ? 'calc(100% - 280px)' : '100%',
      padding: '24px',
      transition: 'all 0.3s ease-in-out',
    };
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
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      
      <Box 
        component="main" 
        sx={{ 
          ...getMainContentStyle(),
          marginTop: '64px', // Account for fixed header
          minHeight: 'calc(100vh - 64px)', // Full height minus header
          background: '#121212',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
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