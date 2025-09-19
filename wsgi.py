#!/usr/bin/env python3
"""
WSGI application file for PythonAnywhere hosting
"""

import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Set working directory
os.chdir(str(project_root))

# Set environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Import the Gradio app
from workflow_project.app import app as gradio_app

# For PythonAnywhere, we need to get the underlying WSGI application
# Gradio apps have a .app attribute that contains the FastAPI/WSGI app
try:
    application = gradio_app.app
except AttributeError:
    # Fallback if the structure is different
    application = gradio_app

if __name__ == "__main__":
    # For testing locally
    gradio_app.launch(server_name="0.0.0.0", server_port=8000)