#!/bin/bash
# Startup script for nuts_vision web interface

echo "=========================================="
echo "nuts_vision - Web Interface Launcher"
echo "=========================================="
echo ""

# Check if PostgreSQL is running (if using Docker)
if command -v docker-compose &> /dev/null; then
    echo "Checking PostgreSQL database..."
    if docker-compose ps | grep -q "nuts_vision_db"; then
        echo "✅ Database container is running"
    else
        echo "⚠️  Database container not running"
        echo "Starting database with docker-compose..."
        docker-compose up -d
        echo "Waiting for database to be ready..."
        sleep 5
    fi
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies ready"
echo ""

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment loaded"
else
    echo "ℹ️  No .env file found, using defaults"
    echo "   Create a .env file based on .env.example for custom configuration"
fi
echo ""

# Launch Streamlit app
echo "=========================================="
echo "🚀 Starting nuts_vision Web Interface..."
echo "=========================================="
echo ""
echo "The application will open in your browser at:"
echo "👉 http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py --server.port 8501 --server.address localhost
