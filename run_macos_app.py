#!/usr/bin/env python3
"""
Launcher script for macOS Coding Assistant
This script creates a standalone macOS app bundle when run using pythonw
"""
import os
import sys
import subprocess
import platform

def main():
    """Launch the application in the most appropriate way for macOS"""
    if platform.system() != "Darwin":
        print("This launcher is designed for macOS only.")
        print(f"Detected platform: {platform.system()}")
        return 1
        
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Set OPENAI_API_KEY from environment if it exists
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        # Check for .env file
        env_path = os.path.join(script_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        # Remove quotes if present
                        if api_key.startswith('"') and api_key.endswith('"'):
                            api_key = api_key[1:-1]
                        os.environ["OPENAI_API_KEY"] = api_key
                        break
    
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment or .env file.")
        print("You will need to set this up for the AI functionality to work.")
    
    print("Starting macOS Discreet Coding Assistant...")
    print("This app will be invisible during screen sharing.")
    print("Use Cmd+Option+C to toggle visibility.")
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # When running via pythonw, create a more app-like experience
    # by not spawning a terminal window
    if "pythonw" in sys.executable:
        # This is running as an "app" without a terminal window
        try:
            from PyQt5.QtWidgets import QApplication
            print("Starting in GUI mode...")
            
            import main
            main.main()
        except ImportError:
            # Fall back to subprocess if PyQt5 can't be imported directly
            subprocess.call([sys.executable.replace("pythonw", "python"), "main.py"])
    else:
        # Running from terminal, just execute the main script directly
        print("Starting from terminal...")
        
        import main
        return main.main()

if __name__ == "__main__":
    sys.exit(main())