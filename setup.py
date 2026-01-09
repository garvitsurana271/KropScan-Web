#!/usr/bin/env python
"""
Setup script for KropScan
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install all required dependencies"""
    print("Installing dependencies...")

    # Install requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("SUCCESS: Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("ERROR: Error installing dependencies from requirements.txt")
        # Try installing packages individually
        packages = [
            "streamlit", "fastapi", "uvicorn", "torch", "torchvision", "timm",
            "Pillow", "requests", "numpy", "opencv-python", "deep-translator",
            "python-multipart", "python-dotenv"
        ]

        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"SUCCESS: {package} installed")
            except subprocess.CalledProcessError:
                print(f"ERROR: Error installing {package}")

def create_sample_data():
    """Create sample data for new features"""
    print("Creating sample data...")

    # Create sample treatment database for offline mode
    sample_treatment_db = {
        "tomato___early_blight": {
            "treatment": "Apply copper-based fungicides immediately."
        },
        "tomato___late_blight": {
            "treatment": "Use Metalaxyl + Mancozeb for emergency treatment."
        },
        "potato___late_blight": {
            "treatment": "Apply Metalaxyl + Mancozeb every 5 days."
        },
        "healthy": {
            "treatment": "No treatment needed. Maintain good farming practices."
        }
    }

    import json
    with open("treatment_database.json", "w", encoding="utf-8") as f:
        json.dump(sample_treatment_db, f)

    print("SUCCESS: Sample treatment database created")

if __name__ == "__main__":
    install_dependencies()
    create_sample_data()
    print("\nSUCCESS: Setup completed! You can now run the application with 'streamlit run frontend.py'")