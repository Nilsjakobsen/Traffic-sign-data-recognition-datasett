#!/bin/bash
# ============================================
# FRONTEND CODE - Development Startup Script
# ============================================
# This script starts both backend and frontend in development mode

echo "🚀 Starting Sign Recognition Web Application..."
echo ""

# Get the project root (two levels up from scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing backend dependencies..."
    pip3 install -r frontend_files/backend/requirements-backend.txt
fi

# Check if frontend dependencies are installed
echo "📦 Checking frontend dependencies..."
if [ ! -d "frontend_files/frontend/node_modules" ]; then
    echo "⚠️  Node modules not found. Installing frontend dependencies..."
    cd frontend_files/frontend && npm install && cd ../..
fi

echo ""
echo "✅ Dependencies ready!"
echo ""
echo "🔧 Starting Flask backend on http://localhost:5000"
echo "🎨 Starting React frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap to kill both processes on exit
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT

# Start Flask backend in background
cd frontend_files/backend || exit 1
python3 app.py &
BACKEND_PID=$!
cd ../.. || exit 1

# Wait a moment for backend to start
sleep 3

# Start React frontend
cd frontend_files/frontend || exit 1
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
