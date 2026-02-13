# Face Attendance Web Application

A modern web application for real-time face detection and attendance tracking with Telegram notifications.

## Features

- **Real-time Face Detection**: Live video stream with face detection overlay
- **Attendance Checking**: One-click attendance check for detected students
- **Database Integration**: SQLite database for storing attendance records
- **Telegram Notifications**: Automatic notifications when attendance is checked
- **Statistics Dashboard**: Charts and graphs showing attendance trends
- **History View**: Detailed attendance history with images
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: Vue.js 3, Nuxt 3, Tailwind CSS
- **Backend**: FastAPI, WebSocket
- **Database**: SQLite
- **Charts**: Chart.js
- **Icons**: Lucide Vue

## Prerequisites

- Node.js 18+ installed
- Python 3.12 with virtual environment
- Face detection backend running (see ../README.md)

## Installation

1. Install dependencies:
```bash
cd web_app
npm install
```

2. Configure environment variables:
```bash
cp ../.env ./.env
```

3. Start the development server:
```bash
npm run dev
```

4. Start the backend dashboard server:
```bash
cd ..
python -m dashboard.server --host 0.0.0.0 --port 8000
```

5. Start the face detection system:
```bash
python -m detection_prod.run_prod --config .\detection_debug\config.example.json
```

## Usage

1. Open http://localhost:3000 in your browser
2. The main page shows real-time face detection
3. Click "Check Attendance" to record attendance for detected students
4. View history and statistics from the navigation menu

## Configuration

Edit the `.env` file to configure:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID
- `API_BASE`: Backend API URL (default: http://localhost:8000)
- `WS_URL`: WebSocket URL (default: ws://localhost:8000/ws)

## Project Structure

```
web_app/
├── components/         # Vue components
│   └── Header.vue
├── pages/             # Nuxt pages
│   ├── index.vue      # Main dashboard
│   ├── history.vue    # Attendance history
│   └── statistics.vue # Statistics charts
├── assets/css/        # Custom CSS
├── package.json       # Dependencies
└── nuxt.config.ts     # Nuxt configuration
```

## API Endpoints

- `GET /api/v1/state` - Get current state
- `POST /api/v1/ingest` - Receive detection data
- `POST /api/v1/attendance/check` - Check attendance
- `GET /api/v1/attendance/history` - Get attendance history
- `WebSocket /ws` - Real-time updates

## Telegram Integration

The system sends notifications to Telegram when:
- Attendance is checked
- Students are detected and recorded

To set up Telegram:
1. Create a bot with @BotFather
2. Get your bot token
3. Get your chat ID
4. Add them to the `.env` file

## Development

To add new features:
1. Create new pages in the `pages/` directory
2. Add components in the `components/` directory
3. Use the API endpoints from the backend

## Production Build

```bash
npm run build
npm start
```
