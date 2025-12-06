# Agri AI Frontend

React frontend for the Agri AI farming management system.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```
   (Use `--legacy-peer-deps` to handle React 19 compatibility)

2. **Start Development Server**
   ```bash
   npm start
   ```
   The app will open at http://localhost:3000

## Features

- 🔐 JWT Authentication (Login/Logout)
- 📊 Dashboard with plot status indicators
- 📈 Plot Detail pages with time-series charts (Chart.js)
- 🚨 Alerts page showing anomalies with AI recommendations
- 🔄 Full API integration with Django backend

## API Configuration

Make sure your Django backend is running at `http://127.0.0.1:8000` (default).
The API base URL is configured in `src/services/api.js`.

## Routes

- `/login` - Login page
- `/dashboard` - Main dashboard (protected)
- `/plot/:plotId` - Plot detail with charts (protected)
- `/alerts` - Anomalies and recommendations (protected)

## Project Structure

```
src/
├── components/       # React components
│   ├── Login.js
│   ├── Dashboard.js
│   ├── PlotDetail.js
│   ├── Alerts.js
│   ├── Navbar.js
│   └── ProtectedRoute.js
├── services/         # API services
│   └── api.js
└── App.js           # Main app with routing
```

