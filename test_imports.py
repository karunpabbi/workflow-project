#!/usr/bin/env python3
"""
Test script to verify the application works before deployment
"""

import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Test imports
try:
    print("Testing imports...")
    from workflow_project.app import app
    print("✅ App import successful!")
    
    from workflow_project.graph import app as graph
    print("✅ Graph import successful!")
    
    from workflow_project.utils import get_fixed_mermaid_data
    print("✅ Utils import successful!")
    
    print("\n🎉 All imports successful! Your app is ready for deployment.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your dependencies and environment setup.")
    sys.exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)