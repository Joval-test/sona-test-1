import React from 'react';
import { Link } from 'react-router-dom';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    padding: "2rem",
    color: "#E0E0E0",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  heroCard: {
    backgroundColor: "#1F1B24",
    borderRadius: "20px",
    padding: "3rem 2.5rem",
    boxShadow: "0 8px 32px rgba(30, 158, 218, 0.2)",
    textAlign: "center",
    maxWidth: "600px",
    border: "1px solid rgb(42, 129, 223)",
    position: "relative",
    overflow: "hidden"
  },
  heroCardBefore: {
    content: '""',
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: "4px",
    background: "linear-gradient(90deg, #FFFFFF 0%, #1E88E5 100%)"
  },
  title: {
    color: "#FFEEEF",
    fontSize: "2.5rem",
    fontWeight: "700",
    marginBottom: "1.5rem",
    letterSpacing: "-0.5px"
  },
  subtitle: {
    color: "#CCCCCC",
    fontSize: "1.1rem",
    lineHeight: "1.6",
    marginBottom: "2.5rem",
    opacity: 0.9
  },
  ctaButton: {
    backgroundColor: "#1E88E5",
    color: "white",
    border: "#000000 2px solid",
    padding: "1rem 2.5rem",
    borderRadius: "25px",
    fontWeight: "600",
    fontSize: "1.1rem",
    cursor: "pointer",
    textDecoration: "none",
    display: "inline-block",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 10px rgba(27, 19, 19, 0.84)",
    transform: "translateY(0)"
  },
  featureGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "1.5rem",
    marginTop: "3rem",
    maxWidth: "900px",
    width: "100%"
  },
  featureCard: {
    backgroundColor: "#1F1B24",
    borderRadius: "12px",
    padding: "1.5rem",
    border: "1px solid #2A3B4D",
    textAlign: "center",
    transition: "all 0.3s ease"
  },
  featureIcon: {
    fontSize: "2.5rem",
    marginBottom: "1rem",
    color: "#FF6347"
  },
  featureTitle: {
    color: "#1E88E5",
    fontSize: "1.1rem",
    fontWeight: "600",
    marginBottom: "0.5rem"
  },
  featureDesc: {
    color: "#CCCCCC",
    fontSize: "0.9rem",
    lineHeight: "1.4"
  }
};

function LandingPage() {
  const features = [
    {
      icon: "🚀",
      title: "AI-Powered Leads",
      description: "Intelligent lead management with automated communication"
    },
    {
      icon: "📊",
      title: "Smart Analytics",
      description: "Comprehensive reporting and insights for better decisions"
    },
    {
      icon: "🔗",
      title: "Seamless Integration",
      description: "Connect with your existing tools and workflows"
    }
  ];

  return (
    <div style={styles.container}>
      <div style={styles.heroCard}>
        <div style={styles.heroCardBefore}></div>
        <h1 style={styles.title}>Welcome to Caze Labs</h1>
        <p style={styles.subtitle}>
          Revolutionizing Lead Management and Business Communication with AI-powered tools. 
          Upload, connect, and manage your business leads and company info with ease.
        </p>
        <Link 
          to="/connect" 
          style={styles.ctaButton}
          onMouseEnter={(e) => {
            e.target.style.transform = "translateY(-2px)";
            e.target.style.boxShadow = "0 6px 20px #1E88E5";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow = "0 4px 15px #1E88E5";
          }}
        >
          Get Started
        </Link>
      </div>

      <div style={styles.featureGrid}>
        {features.map((feature, index) => (
          <div 
            key={index} 
            style={styles.featureCard}
            onMouseEnter={(e) => {
              e.target.style.transform = "translateY(-4px)";
              e.target.style.borderColor = "#1E88E5";
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = "translateY(0)";
              e.target.style.borderColor = "#2A3B4D";
            }}
          >
            <div style={styles.featureIcon}>{feature.icon}</div>
            <h3 style={styles.featureTitle}>{feature.title}</h3>
            <p style={styles.featureDesc}>{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LandingPage;