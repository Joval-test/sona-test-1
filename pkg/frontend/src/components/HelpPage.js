import React from 'react';
import { Box, Typography, Paper, Link } from '@mui/material';
import { Email, Help, Business, Security } from '@mui/icons-material';

const styles = {
  container: {
    backgroundColor: "#121212",
    minHeight: "100vh",
    padding: "2rem",
    color: "#FFFFFF", // White text
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },
  header: {
    color: "#2196F3", // Blue header
    fontSize: "2rem",
    fontWeight: "700",
    marginBottom: "1.5rem",
  },
  card: {
    backgroundColor: "#1E1E2F", // Dark card
    borderRadius: "12px",
    padding: "2rem",
    boxShadow: "0 3px 8px rgba(33, 150, 243, 0.3)", // Blueish glow
    marginBottom: "1.5rem",
  },
  section: {
    marginBottom: "2rem",
  },
  icon: {
    color: "#2196F3", // Blue icons
    marginRight: "1rem",
    verticalAlign: "middle",
  },
  link: {
    color: "#64B5F6", // Light blue link
    textDecoration: "none",
    '&:hover': {
      textDecoration: "underline",
    },
  },
};

function HelpPage() {
  return (
    <Box sx={styles.container}>
      <Typography sx={styles.header}>Help & Support</Typography>
      <Typography sx={{ color: "#CCCCCC", marginBottom: "2rem", textAlign: "center", maxWidth: "800px", margin: "0 auto 2rem" }}>
        Get assistance with using Caze BizConAI. Find answers to common questions, access documentation, and reach out to our support team.
      </Typography>

      <Paper sx={styles.card}>
        <Box sx={styles.section}>
          <Typography variant="h6" sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            <Email sx={styles.icon} />
            Contact Us
          </Typography>
          <Typography sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            For any inquiries or support, please reach out to us at:{' '}
            <Link href="mailto:info@cazelabs.com" sx={styles.link}>info@cazelabs.com</Link>
          </Typography>
        </Box>

        <Box sx={styles.section}>
          <Typography variant="h6" sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            <Help sx={styles.icon} />
            Quick Links
          </Typography>
          <Typography sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            • Getting Started Guide<br />
            • Frequently Asked Questions<br />
            • User Manual<br />
            • Video Tutorials
          </Typography>
        </Box>

        <Box sx={styles.section}>
          <Typography variant="h6" sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            <Business sx={styles.icon} />
            About Us
          </Typography>
          <Typography sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            CazeLabs is dedicated to providing innovative AI solutions for businesses. 
            Our platform helps streamline communication and enhance customer engagement.
          </Typography>
        </Box>

        <Box sx={styles.section}>
          <Typography variant="h6" sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            <Security sx={styles.icon} />
            Privacy & Security
          </Typography>
          <Typography sx={{ color: "#FFFFFF", marginBottom: "1rem" }}>
            We take your privacy and data security seriously. All communications are encrypted 
            and we follow industry-standard security practices to protect your information.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}

export default HelpPage;
