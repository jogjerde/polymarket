#!/usr/bin/env python3
"""
Quick start script for running the Polymarket analysis.
Handles environment setup and execution.
"""

import subprocess
import sys
import os

def main():
    """Run the analyzer."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run main.py
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=False
    )
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
