#!/usr/bin/env python3
"""
Ocean Data Explorer Dashboard Launcher
Automatically installs dependencies and starts the Streamlit dashboard
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        sys.exit(1)

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def main():
    """Main launcher function"""
    print("🌊 Ocean Data Explorer Dashboard Launcher")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    check_python_version()
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        sys.exit(1)
    
    # Install requirements if streamlit is not available
    if not check_streamlit():
        install_requirements()
    
    # Launch Streamlit dashboard
    print("\n🚀 Starting Ocean Data Explorer Dashboard...")
    print("🌐 Open your browser and go to: http://localhost:8501")
    print("⚠️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "ocean_data_dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()