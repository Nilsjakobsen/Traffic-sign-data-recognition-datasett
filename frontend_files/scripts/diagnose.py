"""
Quick diagnostic script to check backend setup
Run from scripts directory: python diagnose.py
"""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("🔍 Backend Diagnostics")
print("=" * 60)
print()

# Check 1: Project paths
print("📁 Path Check:")
print(f"   Script location: {Path(__file__).parent}")
print(f"   Project root: {project_root}")
print(f"   Project root exists: {project_root.exists()}")
print()

# Check 2: Backend directory
backend_dir = project_root / "frontend_files" / "backend"
print(f"📂 Backend directory: {backend_dir}")
print(f"   Exists: {backend_dir.exists()}")
print()

# Check 3: Sign_processing directory
sign_proc_dir = project_root / "Sign_processing"
print(f"📂 Sign_processing: {sign_proc_dir}")
print(f"   Exists: {sign_proc_dir.exists()}")
if sign_proc_dir.exists():
    print(f"   Contents: {list(sign_proc_dir.iterdir())[:5]}")
print()

# Check 4: Model files
model_path = sign_proc_dir / "demo" / "cnn.pth"
classes_path = sign_proc_dir / "demo" / "classes.json"
print(f"🤖 Model files:")
print(f"   cnn.pth: {model_path.exists()} - {model_path}")
print(f"   classes.json: {classes_path.exists()} - {classes_path}")
print()

# Check 5: Import test
print("📦 Import test:")
try:
    from Sign_processing.Map_extractor import MapExtractor, ORB_maps
    print("   ✅ Map_extractor imported")
except Exception as e:
    print(f"   ❌ Map_extractor failed: {e}")

try:
    from Sign_processing.Sign_extractor import Sign_extractor_class
    print("   ✅ Sign_extractor imported")
except Exception as e:
    print(f"   ❌ Sign_extractor failed: {e}")

try:
    from Sign_processing.cnn import CNNPredictor
    print("   ✅ CNNPredictor imported")
except Exception as e:
    print(f"   ❌ CNNPredictor failed: {e}")
print()

# Check 6: temp_uploads directory
temp_uploads = project_root / "temp_uploads"
print(f"📁 Temp uploads: {temp_uploads}")
print(f"   Exists: {temp_uploads.exists()}")
print(f"   Writable: {os.access(temp_uploads.parent, os.W_OK)}")
if not temp_uploads.exists():
    print("   Creating temp_uploads directory...")
    temp_uploads.mkdir(exist_ok=True)
    print(f"   Created: {temp_uploads.exists()}")
print()

# Check 7: Flask
print("🌐 Flask check:")
try:
    import flask
    print(f"   ✅ Flask version: {flask.__version__}")
except Exception as e:
    print(f"   ❌ Flask not found: {e}")
print()

print("=" * 60)
print("✅ Diagnostic complete!")
print("=" * 60)
