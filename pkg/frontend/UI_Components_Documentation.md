# Caze IC Caller AI - UI Components Documentation

## Overview
This document provides a comprehensive guide to all UI components in the Caze IC Caller AI frontend application, their functionality, styling patterns, and usage.

## Design System

### Color Palette
- **Primary Background**: `#121212` - Main application background
- **Secondary Background**: `#1F1B24` - Card and container backgrounds
- **Accent Background**: `#2A3B4D` - Interactive elements and borders
- **Primary Accent**: `#FF6347` (Tomato Red) - Buttons, active states, highlights
- **Secondary Accent**: `#FF4500` (Orange Red) - Gradient endings, hover states
- **Blue Accent**: `#2196F3` - New highlight for active tabs, buttons, and analytics
- **Text Primary**: `#E0E0E0` - Main text content
- **Text Secondary**: `#7A8FA6` - Headers, labels, secondary information
- **Text Muted**: `#CCCCCC` - Placeholder text, disabled states

### Typography
- **Font Family**: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- **Header Sizes**: 1.5rem - 2.5rem with 700 font weight
- **Body Text**: 0.9rem - 1rem with 400-600 font weight
- **Button Text**: 0.9rem - 1rem with 600-700 font weight

### Spacing & Layout
- **Border Radius**: 8px (small), 12px (medium), 16px (cards), 20px (hero), 25px (buttons), 30px (inputs)
- **Padding**: 0.5rem - 3rem based on component size
- **Margins**: 0.5rem - 2rem for component separation
- **Shadows**: `0 3px 8px rgba(33, 150, 243, 0.3)` for cards, `0 8px 32px rgba(30, 158, 218, 0.2)` for hero

## Core Components

### App.js - Main Application Shell
- Sidebar and layout logic unchanged, but blue accent now used for active tab highlights.

### UserChat.js - Customer Chat Interface
- Enhanced dark theme and gradients for header and input area.
- Animated message bubbles with improved alignment and color contrast.
- Loading and error states visually distinct.
- Auto-scroll and responsive textarea with max height.

### ConnectDashboard.js - Lead Management
- Card-based layout with blue accent shadows.
- Search and filter UI improved for clarity.
- Bulk actions and status badges styled with blue accent.
- Responsive, flex-based table rows and headers.

### ReportPage.js - Analytics Dashboard
- Filter buttons now use blue accent for active state.
- Card and link buttons updated to blue accent.
- Expanded content and search input styled for clarity.

### SettingsPage.js - Configuration Hub
- Tabbed navigation uses blue accent for active tab.
- Content cards and danger zone styled with blue accent and larger border radius.
- All settings forms use consistent dark theme and spacing.

### AdminChatReview.js - Chat History Management
- Uses dark theme with red and blue gradients for buttons.
- Enhanced form controls and feedback alerts.
- Paper/card elements styled for clarity and separation.

### AdminLogin.js - Authentication Interface
- Card and button styling updated for consistency.
- Error and loading states visually improved.

### LandingPage.js - Public Homepage
- Hero card and feature grid use blue accent and larger border radii.
- CTA button and feature highlights updated for clarity and contrast.

## Settings Components

### EmailSettings.js
- Dark theme, blue accent for focus and buttons.
- Success/error alerts styled for clarity.
- Right-aligned save button with loading state.

### AzureSettings.js
- Dark theme, red accent for focus, blue for buttons.
- All fields center-aligned, with clear feedback alerts.

### PrivateLinkSettings.js
- Dark theme, blue accent for buttons.
- Form fields and save button right-aligned.

### CompanyInfoSettings.js
- Drag-and-drop PDF upload zone with visual feedback.
- Alerts for upload status.
- Blue accent for buttons and focus.

### LeadsInfoSettings.js
- Drag-and-drop Excel/CSV upload zone with visual feedback.
- Alerts for upload status.
- Blue accent for upload button and focus.

## Dashboard Components

### ConnectDashboard.js
- See above (Core Components) for details.

### UserDashboard.js
- Card-based layout with loading spinner and message display.
- Consistent dark theme and accent usage.

## Styling Patterns

### Card Components
```css
backgroundColor: "#1F1B24"
borderRadius: "12px" (cards), "16px" (content/danger zone), "20px" (hero)
padding: "1.5rem" to "3rem"
boxShadow: "0 3px 8px rgba(33, 150, 243, 0.3)" (blue accent)
border: "1px solid #2A3B4D" or "1px solid #2196F3" (blue accent)