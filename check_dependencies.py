#!/usr/bin/env python3
"""
Check if all required dependencies are installed.
"""

import sys
import subprocess


def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = [
        'ultralytics',
        'torch',
        'cv2',
        'numpy',
        'pytesseract',
        'pandas',
        'matplotlib',
        'seaborn',
        'PIL',
        'yaml'
    ]
    
    missing = []
    installed = []
    
    print("Checking Python packages...")
    for package in required_packages:
        try:
            __import__(package)
            installed.append(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ✗ {package} - NOT INSTALLED")
    
    return missing, installed


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("\nChecking Tesseract OCR...")
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  ✓ {version}")
            return True
        else:
            print("  ✗ Tesseract not found")
            return False
    except FileNotFoundError:
        print("  ✗ Tesseract not found")
        return False


def main():
    print("="*60)
    print("nuts_vision - Dependency Check")
    print("="*60 + "\n")
    
    # Check Python packages
    missing_packages, installed_packages = check_python_packages()
    
    # Check Tesseract
    tesseract_ok = check_tesseract()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if missing_packages:
        print("\n❌ Missing Python packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nTo install missing packages, run:")
        print("   pip install -r requirements.txt")
    else:
        print("\n✓ All Python packages installed!")
    
    if not tesseract_ok:
        print("\n❌ Tesseract OCR not found")
        print("\nTo install Tesseract:")
        print("   Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("   macOS: brew install tesseract")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    else:
        print("\n✓ Tesseract OCR installed!")
    
    # Return status
    if missing_packages or not tesseract_ok:
        print("\n⚠ Some dependencies are missing. Please install them before using nuts_vision.")
        return 1
    else:
        print("\n✓ All dependencies satisfied! You're ready to use nuts_vision.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
