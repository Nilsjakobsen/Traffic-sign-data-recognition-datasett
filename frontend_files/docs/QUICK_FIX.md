# 🔧 Quick Fix: Installation Issues

## Issue: pip install command error

### ❌ Wrong Command:
```bash
pip install -r requirements.txt requirements-backend.txt
```

### ✅ Correct Command:
```bash
# Install each file separately
pip install -r requirements.txt
pip install -r requirements-backend.txt
```

---

## Issue: npm not found

If you see: `Command 'npm' not found`

### Solution: Install Node.js

**Ubuntu/Debian/WSL:**
```bash
sudo apt update
sudo apt install nodejs npm
```

**Verify installation:**
```bash
node --version
npm --version
```

---

## 🚀 Complete Installation Steps (Copy-Paste Ready)

### Step 1: Backend Dependencies
```bash
cd /home/oskar/Sign_recognition_project
pip install -r requirements.txt
pip install -r requirements-backend.txt
```

### Step 2: Install Node.js (if needed)
```bash
sudo apt update
sudo apt install nodejs npm
```

### Step 3: Frontend Dependencies
```bash
cd /home/oskar/Sign_recognition_project/frontend
npm install
cd ..
```

### Step 4: Test Backend
```bash
python test_backend.py
```

### Step 5: Start Application

**Option A: Easy way (automatic)**
```bash
./start-dev.sh
```

**Option B: Manual (two terminals)**

Terminal 1 - Backend:
```bash
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Then open: http://localhost:3000

---

## ✅ Current Status

Based on your terminal output:
- ✅ Python environment active (ikt213)
- ✅ Flask and dependencies installed
- ❌ Node.js/npm not installed yet

### Next Steps:

1. **Install Node.js:**
   ```bash
   sudo apt install nodejs npm
   ```

2. **Install frontend dependencies:**
   ```bash
   cd /home/oskar/Sign_recognition_project/frontend
   npm install
   ```

3. **Start the app:**
   ```bash
   cd /home/oskar/Sign_recognition_project
   python app.py
   ```
   
   Then in another terminal:
   ```bash
   cd /home/oskar/Sign_recognition_project/frontend
   npm run dev
   ```

---

## 🆘 Still Having Issues?

### Check Python packages:
```bash
pip list | grep -E "Flask|opencv|torch|pdf2image"
```

### Check if required files exist:
```bash
ls -la Sign_processing/demo/cnn.pth
ls -la Sign_processing/demo/classes.json
```

### Test just the backend:
```bash
python app.py
# Should see: "Running on http://127.0.0.1:5000"
# Press Ctrl+C to stop
```

---

## 📝 Notes

- You're using conda environment `ikt213` - that's perfect!
- Keep that environment activated when running Python commands
- Frontend (npm) doesn't need the conda environment
- Backend must be on port 5000, frontend on port 3000
