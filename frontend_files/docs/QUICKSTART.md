# 🚦 Sign Recognition Web Application - Quick Start Guide

## What is this?

A web application that extracts and identifies traffic signs from PDF documents containing traffic plans. Upload a PDF, get back a list of detected signs with their classifications and confidence scores.

## Quick Start (3 steps!)

### 1️⃣ Install Dependencies

**Backend (Python):**
```bash
# Install each requirements file separately
pip install -r requirements.txt
pip install -r requirements-backend.txt

# Note: If using conda, make sure your environment is activated first
```

**Frontend (Node.js):**

First, install Node.js if you haven't already:
```bash
# Ubuntu/Debian
sudo apt install nodejs npm

# Or download from: https://nodejs.org/
```

Then install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### 2️⃣ Start the Application

**Option A: Use the startup script (Recommended)**

Linux/Mac:
```bash
./start-dev.sh
```

Windows:
```bash
start-dev.bat
```

**Option B: Manual start**

Terminal 1 - Backend:
```bash
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 3️⃣ Use the Application

1. Open browser: `http://localhost:3000`
2. Upload a PDF file
3. Click "Process PDF"
4. View results and download CSV

## 📁 What was added for the frontend?

All frontend code is clearly marked with comments:

### New Files Created:
```
app.py                          # ← Flask backend (FRONTEND CODE)
requirements-backend.txt        # ← Backend dependencies (FRONTEND CODE)
frontend/                       # ← ALL FRONTEND CODE
  ├── package.json
  ├── vite.config.js
  ├── index.html
  └── src/
      ├── main.jsx
      ├── App.jsx
      ├── App.css
      ├── index.css
      └── components/
          ├── FileUpload.jsx
          ├── SignList.jsx
          └── SignCard.jsx
start-dev.sh                    # ← Startup script (FRONTEND CODE)
start-dev.bat                   # ← Windows startup script (FRONTEND CODE)
FRONTEND_README.md              # ← Detailed docs (FRONTEND CODE)
QUICKSTART.md                   # ← This file (FRONTEND CODE)
```

### Modified Files:
```
.gitignore                      # ← Added frontend ignore rules (marked with FRONTEND CODE comments)
```

### Not Modified:
```
main.py                         # ← Original pipeline (unchanged)
Sign_processing/                # ← Original code (unchanged)
requirements.txt                # ← Original dependencies (unchanged)
```

## 🎯 How it Works

1. **Upload**: User uploads PDF through React interface
2. **Backend Processing**: Flask receives PDF and runs it through your existing pipeline:
   - `MapExtractor` extracts pages from PDF
   - `Sign_extractor_class` detects signs in each page
   - `CNNPredictor` classifies each detected sign
3. **Results**: React displays signs with classifications and confidence scores
4. **Export**: User can download results as CSV

## 📊 Features

- ✅ Drag-and-drop file upload
- ✅ Real-time processing feedback
- ✅ Visual sign previews
- ✅ Confidence scores with color coding
- ✅ CSV export
- ✅ Responsive design (mobile-friendly)
- ✅ Session-based file handling

## 🔧 Configuration

### Change Backend Port
In `app.py` (last line):
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

### Change Frontend Port
In `frontend/vite.config.js`:
```javascript
server: {
  port: 3000,  // Change port here
}
```

### Adjust File Size Limit
In `app.py`:
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB - adjust as needed
```

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt requirements-backend.txt`
- Check port 5000 is available

**Frontend won't start:**
- Check Node.js version (16+)
- Run `npm install` in frontend directory
- Check port 3000 is available

**No signs detected:**
- Verify PDF contains actual images (not just text)
- Check model files exist in `Sign_processing/demo/`
- Look at Flask terminal for error messages

**CORS errors:**
- Make sure both backend and frontend are running
- Check that frontend is configured to proxy to backend

## 📖 More Information

For detailed documentation, see `FRONTEND_README.md`

## 🎉 That's it!

Your sign recognition system now has a user-friendly web interface!
