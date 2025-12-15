# 🔧 Fixing "Input/output error" - Quick Guide

## The Problem

You're seeing: `Processing failed: [Errno 5] Input/output error`

This means the **Flask backend is not running** or has crashed. The React frontend can't reach it.

## Quick Fix

### Step 1: Make sure Flask backend is running

Open a terminal and run:

```bash
cd /home/oskar/Sign_recognition_project/frontend_files/backend

# Activate conda environment (IMPORTANT!)
conda activate ikt213

# Start Flask
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

**Keep this terminal open!**

### Step 2: Make sure React frontend is running

Open a **NEW** terminal and run:

```bash
cd /home/oskar/Sign_recognition_project/frontend_files/frontend

# Start React
npm run dev
```

You should see:
```
VITE ready in XXXms
Local: http://localhost:3000/
```

**Keep this terminal open too!**

### Step 3: Refresh your browser

Go to http://localhost:3000 and try uploading again.

---

## Even Easier Way - Use the Script

I created a new script that handles conda activation:

```bash
cd /home/oskar/Sign_recognition_project/frontend_files/scripts
./quick-start.sh
```

This will:
- ✅ Activate conda environment automatically
- ✅ Check all dependencies
- ✅ Start both backend and frontend
- ✅ Handle Ctrl+C gracefully

---

## Common Issues

### "ModuleNotFoundError: No module named 'flask'"
**Solution:** Activate conda environment first!
```bash
conda activate ikt213
pip install -r frontend_files/backend/requirements-backend.txt
```

### Backend starts but immediately crashes
**Solution:** Check the terminal for errors. Common causes:
- Missing model files in `Sign_processing/demo/`
- Permission issues with `temp_uploads/` directory

Create temp_uploads if needed:
```bash
mkdir -p /home/oskar/Sign_recognition_project/temp_uploads
```

### Frontend can't connect (ECONNREFUSED)
**Solution:** Backend isn't running. Start it first (see Step 1 above).

---

## Verify Everything is Working

Run these commands to check:

```bash
# Test 1: Check if backend is running
curl http://localhost:5000/api/health
# Should return: {"status":"healthy"}

# Test 2: Check if frontend is running
curl http://localhost:3000
# Should return HTML

# Test 3: Both should be running in separate terminals
ps aux | grep "python app.py"
ps aux | grep "vite"
```

---

## Current Running Order

✅ **What you need running:**

1. **Terminal 1:** Flask backend on port 5000
2. **Terminal 2:** React frontend on port 3000
3. **Browser:** Open http://localhost:3000

❌ **What went wrong:** Backend wasn't running with conda environment activated

---

## Quick Reference

### Start Backend (Terminal 1):
```bash
cd /home/oskar/Sign_recognition_project/frontend_files/backend
conda activate ikt213
python app.py
```

### Start Frontend (Terminal 2):
```bash
cd /home/oskar/Sign_recognition_project/frontend_files/frontend
npm run dev
```

### Or use the automated script:
```bash
cd /home/oskar/Sign_recognition_project/frontend_files/scripts
./quick-start.sh
```

---

**Note:** The "Input/output error" appears because the frontend tries to upload to the backend, but the backend isn't responding (not running).
