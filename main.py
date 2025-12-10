"""Main entry point for the application."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Streamlit not found. Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run streamlit app
    app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
    subprocess.run(["streamlit", "run", str(app_path)])

