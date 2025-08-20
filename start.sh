#!/bin/bash

# Personal Finance Tracker - Startup Script
# This script ensures clean database state and starts the application

echo "=================================================="
echo "Personal Finance Tracker - Starting Application"
echo "=================================================="

# Set environment variables for production
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5000}

echo "Environment: $FLASK_ENV"
echo "Port: $PORT"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Initialize database (only if needed)
echo "Checking database..."
# Database initialization is now handled in app.py

echo ""
echo "Starting Flask application..."
echo "Access the app at: http://localhost:$PORT"
echo "=================================================="

# Start the application
if [ "$FLASK_ENV" = "production" ]; then
    # Use gunicorn for production
    if command -v gunicorn &> /dev/null; then
        gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
    else
        echo "Gunicorn not found. Installing..."
        pip install gunicorn
        gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
    fi
else
    # Use Flask development server
    python app.py
fi
