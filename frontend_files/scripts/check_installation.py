#!/usr/bin/env python3
"""
============================================
FRONTEND CODE - Installation Checker
============================================
Run this script to verify all dependencies are installed correctly
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro}")
        print(f"   Need Python 3.8 or higher")
        return False

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_python_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking Python dependencies...")
    
    required = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'torch': 'torch',
        'torchvision': 'torchvision',
        'pdf2image': 'pdf2image',
        'pytesseract': 'pytesseract'
    }
    
    missing = []
    for module, package in required.items():
        if check_python_package(module):
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   To install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def check_node():
    """Check if Node.js is installed"""
    print("\n🟢 Checking Node.js...")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        print(f"   ✅ Node.js {version}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Node.js not found")
        print("   Install from: https://nodejs.org/")
        return False

def check_npm():
    """Check if npm is installed"""
    print("\n📦 Checking npm...")
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        print(f"   ✅ npm {version}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ npm not found")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    print("\n🎨 Checking frontend dependencies...")
    
    node_modules = Path("frontend/node_modules")
    package_json = Path("frontend/package.json")
    
    if not package_json.exists():
        print("   ❌ frontend/package.json not found")
        return False
    
    if not node_modules.exists():
        print("   ⚠️  node_modules not found")
        print("   Run: cd frontend && npm install")
        return False
    
    # Check for key packages
    key_packages = ['react', 'vite', 'axios']
    missing = []
    for pkg in key_packages:
        if not (node_modules / pkg).exists():
            missing.append(pkg)
    
    if missing:
        print(f"   ⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: cd frontend && npm install")
        return False
    
    print("   ✅ Frontend dependencies installed")
    return True

def check_model_files():
    """Check if model files exist"""
    print("\n🤖 Checking model files...")
    
    model_path = Path("Sign_processing/demo/cnn.pth")
    classes_path = Path("Sign_processing/demo/classes.json")
    
    all_good = True
    
    if model_path.exists():
        print(f"   ✅ {model_path}")
    else:
        print(f"   ❌ {model_path} (missing)")
        all_good = False
    
    if classes_path.exists():
        print(f"   ✅ {classes_path}")
    else:
        print(f"   ❌ {classes_path} (missing)")
        all_good = False
    
    return all_good

def check_directory_structure():
    """Check if key directories exist"""
    print("\n📁 Checking directory structure...")
    
    required_dirs = [
        "Sign_processing",
        "frontend",
        "frontend/src",
        "frontend/src/components"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (missing)")
            all_good = False
    
    return all_good

def check_required_files():
    """Check if required files exist"""
    print("\n📄 Checking required files...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "requirements-backend.txt",
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/src/App.jsx",
        "frontend/src/main.jsx"
    ]
    
    all_good = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_good = False
    
    return all_good

def main():
    """Run all checks"""
    print("=" * 70)
    print("Sign Recognition Web Application - Installation Checker")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", check_python_dependencies),
        ("Node.js", check_node),
        ("npm", check_npm),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Frontend Dependencies", check_frontend_dependencies),
        ("Model Files", check_model_files)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error checking {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print("🎉 All checks passed! You're ready to go!")
        print("\nTo start the application:")
        print("  ./start-dev.sh        (Linux/Mac)")
        print("  start-dev.bat         (Windows)")
        print("\nOr manually:")
        print("  Terminal 1: python app.py")
        print("  Terminal 2: cd frontend && npm run dev")
    else:
        print(f"⚠️  {total - passed} check(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  pip install -r requirements.txt requirements-backend.txt")
        print("  cd frontend && npm install")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
