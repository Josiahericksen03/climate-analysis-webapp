#!/usr/bin/env python3
"""
WSGI entry point for the Climate Analysis Web Application
"""

import os
import sys

# Add the webapp directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    app.run() 