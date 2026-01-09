#!/usr/bin/env python
"""
KropScan Application Runner
This script ensures all dependencies are available and runs the application
"""

import sys
import subprocess
import os

def check_and_install_dependencies():
    """Check if dependencies are installed, install if not"""
    try:
        import streamlit
        import torch
        import torchvision
        import timm
        import requests
        import numpy
        import cv2
        import PIL
        import groq
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def run_application():
    """Run the KropScan application"""
    print("\n🚀 Starting KropScan Application...")
    print("🌐 Access the application at: http://localhost:8501")
    print("💡 Note: Make sure backend.py is running in another terminal")
    
    try:
        # Run streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend.py"])
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    print("🌾 KropScan - AI-Powered Crop Disease Detection")
    print("="*50)
    
    if check_and_install_dependencies():
        run_application()
    else:
        print("\n❌ Could not start application due to missing dependencies")
        print("Please install dependencies manually using: pip install -r requirements.txt")