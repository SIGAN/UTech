#!/usr/bin/env python3
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import init_db

if __name__ == "__main__":
    # Ensure we're in the correct working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")