# 🎨 Frontend Files

This directory contains all frontend-related files for the Sign Recognition web application.

## 📁 Directory Structure

```
frontend_files/
├── backend/                    # Flask backend API
│   ├── app.py                 # Flask server
│   └── requirements-backend.txt
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── scripts/                    # Helper scripts
│   ├── start-dev.sh           # Linux/Mac startup
│   ├── start-dev.bat          # Windows startup
│   ├── check_installation.py  # Verify setup
│   ├── test_backend.py        # API testing
│   └── demo_upload.py         # Demo script
│
└── docs/                       # Documentation
    ├── GET_STARTED.md         # Getting started guide
    ├── QUICKSTART.md          # Quick setup
    ├── FRONTEND_README.md     # Detailed docs
    ├── ARCHITECTURE.md        # System design
    ├── API_EXAMPLES.md        # API usage
    └── ...
```

## 🚀 Quick Start

### From Project Root:

```bash
# 1. Install backend dependencies
pip install -r requirements.txt
pip install -r frontend_files/backend/requirements-backend.txt

# 2. Install frontend dependencies
cd frontend_files/frontend
npm install
cd ../..

# 3. Start backend
cd frontend_files/backend
python app.py
# Keep this terminal running

# 4. Start frontend (new terminal)
cd frontend_files/frontend
npm run dev
# Keep this terminal running

# 5. Open browser
# http://localhost:3000
```

### Or use the helper script:

```bash
cd frontend_files/scripts
./start-dev.sh
```

## 📖 Documentation

See `docs/GET_STARTED.md` for complete setup instructions.

## 🎯 Features

- **Backend**: Flask API that processes PDFs through the sign recognition pipeline
- **Frontend**: React web app with table and grid views
- **Helper Scripts**: Automated setup and testing tools
- **Documentation**: Comprehensive guides for setup and usage

## 🔧 Important Paths

When running scripts, make sure to update paths to reference the new structure:
- Backend: `frontend_files/backend/app.py`
- Frontend: `frontend_files/frontend/`
- Model files: `../Sign_processing/demo/` (unchanged)

## ✨ What's Here

All files in this directory are frontend-related code:
- Marked with "FRONTEND CODE" comments
- Created to provide web interface for the sign recognition system
- Original pipeline code (`main.py`, `Sign_processing/`) remains in project root

---

**Note**: This is a reorganized structure. The original files work the same, just in a cleaner layout!
