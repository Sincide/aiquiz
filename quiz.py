#!/usr/bin/env python3
"""
CISSP Quiz Application Launcher
Simple script to start the quiz application
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from quiz_app.main import main
    
    if __name__ == '__main__':
        print("Starting CISSP Quiz Application...")
        main()
        
except ImportError as e:
    print(f"Error importing quiz application: {e}")
    print("Make sure you're in the correct directory and all files are present.")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nQuiz application interrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"Error running quiz application: {e}")
    sys.exit(1) 