#!/bin/bash

echo "========================================="
echo "Aldar Köse Storyboard Generator"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your OpenAI API key:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run the application
echo "Starting server..."
echo "Visit: http://localhost:8080"
echo ""
echo "Note: Using port 8080 to avoid conflict with macOS AirPlay"
echo "Press Ctrl+C to stop"
echo ""

python app.py
