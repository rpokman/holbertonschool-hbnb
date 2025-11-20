# Part 4 - Simple Web Client 🌐

## Overview

Complete web client for the HBnB application with authentication, dynamic content, and modern UI features.

## Features

### Authentication
- JWT-based login system
- Secure token storage in cookies
- Password visibility toggle
- Automatic redirect for protected pages

### Pages

#### Login Page (`login.html`)
- Email and password authentication
- Form validation
- Error handling
- Redirect to index after successful login

#### Index Page (`index.html`)
- Dynamic place listing from API
- Price filtering ($10, $50, $100, $150, $200+)
- Real-time filter without page reload
- Authenticated/Guest mode

#### Place Details Page (`place.html`)
- Complete place information
- Owner details
- Amenities with icons (📶 WiFi, 🛁 Bath, 🛏️ Bed)
- User reviews with ratings
- Review submission form (authenticated users only)

### Theme System

6 customizable themes with persistent storage:
- **Red Theme** (Light/Dark)
- **Forest Theme** (Light/Dark)
- **Ocean Theme** (Light/Dark)

Features:
- CSS variables for easy customization
- Logo icon changes with theme
- Cookie-based preference storage
- Smooth transitions

## Technical Stack

- **Frontend**: Vanilla JavaScript ES6, HTML5, CSS3
- **API**: Flask REST API (port 5000)
- **Authentication**: JWT tokens (3600s expiry)
- **Storage**: Cookies for tokens and theme preferences
- **Design**: Responsive, mobile-friendly

## File Structure

```
part4/
├── index.html          # Places list page
├── login.html          # Authentication page
├── place.html          # Place details page
├── scripts.js          # Application logic
├── styles.css          # Styling and themes
└── images/
    ├── red_icon.png    # Red theme logo
    ├── green_icon.png  # Forest theme logo
    └── blue_icon.png   # Ocean theme logo
```

## Setup

1. Start the Flask API server (part3):
```bash
cd ../part3
source /root/Holberton/.venv/bin/activate
flask run
```

2. Start the web client:
```bash
cd ../part4
python3 -m http.server 8080
```

3. Access the application:
```
http://localhost:8080/index.html
```

## Authentication

### Default Users

**Admin:**
- Email: `admin@hbnb.com`
- Password: `admin1234`

**Test User:**
- Email: `testuser@hbnb.com`
- Password: `password123`

## API Endpoints Used

- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/places/` - List all places
- `GET /api/v1/places/<id>` - Get place details
- `POST /api/v1/reviews/` - Submit review (authenticated)

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari

## Security

- JWT tokens stored in HTTP-only cookies
- Token expiry: 1 hour
- Protected routes redirect to index if not authenticated
- CORS configured for localhost development