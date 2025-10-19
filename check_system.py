#!/usr/bin/env python3
"""
System Requirements Checker for Aldar Köse Storyboard Generator
Run this before installation to verify your system meets requirements
"""

import sys
import os
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_check(status, message):
    """Print a check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_check(is_valid, f"Python version: {version_str}")
    
    if not is_valid:
        print("   ⚠️  Python 3.8+ required. Please upgrade Python.")
        print("   Download from: https://www.python.org/downloads/")
    
    return is_valid

def check_pip():
    """Check if pip is installed"""
    try:
        import pip
        print_check(True, f"pip is installed (version {pip.__version__})")
        return True
    except ImportError:
        print_check(False, "pip is not installed")
        print("   ⚠️  Install pip: python -m ensurepip --upgrade")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_check(True, ".env file exists")
        
        # Check if it has an API key
        try:
            with open(env_file) as f:
                content = f.read()
                if "OPENAI_API_KEY=sk-" in content or "OPENAI_API_KEY=your" in content:
                    if "your_openai_api_key_here" in content:
                        print("   ⚠️  Remember to replace placeholder with your actual API key!")
                        return False
                    else:
                        print("   ✓ API key appears to be configured")
                        return True
                else:
                    print("   ⚠️  No valid API key found in .env")
                    return False
        except Exception as e:
            print(f"   ⚠️  Error reading .env: {e}")
            return False
    else:
        print_check(False, ".env file does not exist")
        if env_example.exists():
            print("   → Run: cp .env.example .env")
            print("   → Then edit .env and add your OpenAI API key")
        else:
            print("   ⚠️  .env.example file is also missing!")
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "static/generated",
        "static/exports",
        "static/css",
        "static/js",
        "templates",
        "models"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        exists = path.exists()
        if not exists:
            all_exist = False
            print_check(False, f"Directory missing: {dir_path}")
            print(f"   → Will be created automatically on first run")
        
    if all_exist:
        print_check(True, "All required directories exist")
    
    return True  # Not critical, will be created

def check_port_availability():
    """Check if port 8080 is available"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        
        if result == 0:
            print_check(False, "Port 8080 is in use")
            print("   ⚠️  Another application is using port 8080")
            print("   → Stop the other application or change port in app.py")
            return False
        else:
            print_check(True, "Port 8080 is available")
            return True
    except Exception as e:
        print_check(False, f"Could not check port availability: {e}")
        return False

def check_required_files():
    """Check if essential files exist"""
    required_files = [
        "app.py",
        "storyboard_generator.py",
        "requirements.txt",
        "templates/index.html"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        exists = path.exists()
        if not exists:
            all_exist = False
            print_check(False, f"Missing required file: {file_path}")
    
    if all_exist:
        print_check(True, "All required files present")
    
    return all_exist

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)  # Convert to GB
        
        if free_gb < 1:
            print_check(False, f"Low disk space: {free_gb}GB free")
            print("   ⚠️  At least 1GB free space recommended")
            return False
        else:
            print_check(True, f"Disk space: {free_gb}GB free")
            return True
    except Exception as e:
        print_check(False, f"Could not check disk space: {e}")
        return True  # Not critical

def get_os_info():
    """Get operating system information"""
    os_name = platform.system()
    os_version = platform.release()
    print_check(True, f"Operating System: {os_name} {os_version}")
    
    if os_name == "Darwin":  # macOS
        print("   💡 macOS detected - port 5000 may conflict with AirPlay")
        print("   → This app uses port 8080 by default")
    
    return True

def main():
    """Run all system checks"""
    print_header("Aldar Köse Storyboard Generator - System Check")
    print("\nThis script checks if your system meets the requirements.")
    
    # Run all checks
    checks = {
        "Python Version": check_python_version(),
        "pip": check_pip(),
        "Operating System": get_os_info(),
        ".env Configuration": check_env_file(),
        "Required Files": check_required_files(),
        "Directories": check_directories(),
        "Port 8080": check_port_availability(),
        "Disk Space": check_disk_space()
    }
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if all(checks.values()):
        print("\n🎉 All checks passed! You're ready to install and run the app.")
        print("\nNext steps:")
        print("  1. pip install -r requirements.txt")
        print("  2. python app.py")
        print("  3. Open http://localhost:8080")
    elif checks["Python Version"] and checks["pip"]:
        print("\n⚠️  Some checks failed, but you can proceed with installation.")
        print("    Missing directories and files will be created automatically.")
        print("\n❗ Important:")
        if not checks[".env Configuration"]:
            print("  • Configure your .env file with OpenAI API key")
        if not checks["Port 8080"]:
            print("  • Free up port 8080 or change port in app.py")
        
        print("\nOnce fixed, run:")
        print("  pip install -r requirements.txt")
        print("  python app.py")
    else:
        print("\n❌ Critical requirements missing. Please fix the errors above.")
        print("\nRequired:")
        print("  • Python 3.8+")
        print("  • pip package manager")
    
    print("\n" + "=" * 70)
    return all(checks.values())

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
