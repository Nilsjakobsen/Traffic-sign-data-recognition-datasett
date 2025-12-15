#!/bin/bash
# ============================================
# FRONTEND CODE - Quick Start Script
# ============================================
# Run this from the scripts directory to start everything

echo "🚀 Starting Sign Recognition Application"
echo ""

# Get to project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "📂 Project root: $PROJECT_ROOT"
echo ""

# Check conda environment
if command -v conda &> /dev/null; then
    echo "🐍 Activating conda environment 'ikt213'..."
    eval "$(conda shell.bash hook)"
    conda activate ikt213 || {
        echo "⚠️  Could not activate ikt213 environment"
        echo "Make sure you've created it or adjust the environment name"
    }
fi

# Check Flask
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed in current environment"
    echo "Run: pip install -r $PROJECT_ROOT/frontend_files/backend/requirements-backend.txt"
    exit 1
fi

# Check Node
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found"
    echo "Install: sudo apt install nodejs npm"
    exit 1
fi

# Check frontend dependencies
if [ ! -d "$PROJECT_ROOT/frontend_files/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd "$PROJECT_ROOT/frontend_files/frontend"
    npm install
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🔧 Starting Flask backend on http://localhost:5000"
echo "   (Close with Ctrl+C)"
echo ""

# Start backend
cd "$PROJECT_ROOT/frontend_files/backend"
python app.py &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 3

echo ""
echo "🎨 Starting React frontend on http://localhost:3000"
echo "   (Close with Ctrl+C)"
echo ""

# Start frontend
cd "$PROJECT_ROOT/frontend_files/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers started!"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🌐 Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Handle Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
