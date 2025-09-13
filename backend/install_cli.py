#!/usr/bin/env python3
"""
Install CLI for Quantum Code Inspector
"""

import subprocess
import sys
import os
from pathlib import Path

def install_cli():
    """Install the CLI in development mode"""
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    try:
        # Install in development mode
        print("🔧 Installing Quantum Code Inspector CLI...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CLI installed successfully!")
            print("\nYou can now use:")
            print("  quantum-inspector analyze <path>")
            print("  qci analyze <path>")
            print("  quantum-inspector --help")
        else:
            print("❌ Installation failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Installation error: {e}")

if __name__ == "__main__":
    install_cli()
