#!/usr/bin/env python3
"""
Create Combined App Script

This script wraps together all the necessary functionality into a single,
easy-to-run Python script that will:

1. Check for required dependencies
2. Install any missing dependencies
3. Create a proper macOS .app bundle 
4. Create a DMG installer file

This makes it simple for the user to create a distributable app.
"""
import os
import sys
import platform
import subprocess
import time
import tempfile
import shutil
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "PyQt5",
        "openai",
        "pyobjc-core",
        "pyobjc-framework-Cocoa",
        "pyobjc-framework-Quartz",
        "pynput"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.split('-')[0].lower())
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing dependencies: {', '.join(missing_packages)}")
        return False, missing_packages
    
    return True, []

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    print(f"Installing missing dependencies: {', '.join(missing_packages)}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", *missing_packages
        ], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def check_api_key():
    """Check if OpenAI API key is set"""
    if "OPENAI_API_KEY" not in os.environ:
        print("⚠️ Warning: OPENAI_API_KEY environment variable not found.")
        print("This is required for the app to function properly.")
        
        key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if key:
            os.environ["OPENAI_API_KEY"] = key
            print("API key set for this session.")
            
            # Ask if user wants to save the key
            save = input("Save this API key to your shell profile? (y/n): ").lower()
            if save == 'y':
                home = os.path.expanduser("~")
                
                # Determine profile file based on shell
                shell = os.environ.get("SHELL", "")
                if "zsh" in shell:
                    profile = os.path.join(home, ".zshrc")
                else:
                    profile = os.path.join(home, ".bash_profile")
                
                # Append to profile
                with open(profile, "a") as f:
                    f.write(f"\n# Added by StealthAI\nexport OPENAI_API_KEY='{key}'\n")
                
                print(f"API key saved to {profile}")
                print(f"Please run 'source {profile}' or restart your terminal.")
        else:
            print("Continuing without API key. The app will prompt for it later.")

def create_app_bundle():
    """Create a macOS app bundle"""
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("Error: App bundle creation is only supported on macOS.")
        return False
    
    try:
        print("Creating macOS .app bundle...")
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define the app bundle structure
        app_name = "StealthAI.app"
        app_path = os.path.join(current_dir, app_name)
        
        # Remove existing app if it exists
        if os.path.exists(app_path):
            print(f"Removing existing app bundle: {app_path}")
            shutil.rmtree(app_path)
        
        # Create the directory structure
        os.makedirs(os.path.join(app_path, "Contents", "MacOS"), exist_ok=True)
        os.makedirs(os.path.join(app_path, "Contents", "Resources"), exist_ok=True)
        
        # Create Info.plist
        with open(os.path.join(app_path, "Contents", "Info.plist"), "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StealthAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.stealthai.app</string>
    <key>CFBundleName</key>
    <string>StealthAI</string>
    <key>CFBundleDisplayName</key>
    <string>StealthAI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>StealthAI needs to control system events for keyboard shortcuts.</string>
    <key>NSScreenCaptureUsageDescription</key>
    <string>StealthAI needs to capture the screen to analyze coding problems.</string>
</dict>
</plist>""")
        
        # Create launcher script
        launcher_path = os.path.join(app_path, "Contents", "MacOS", "StealthAI")
        with open(launcher_path, "w") as f:
            f.write("""#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../Resources"
./stealth_overlay
""")
        os.chmod(launcher_path, 0o755)
        
        # Copy stealth_overlay.py to Resources
        overlay_src = os.path.join(current_dir, "stealth_overlay.py")
        overlay_dest = os.path.join(app_path, "Contents", "Resources", "stealth_overlay")
        
        # Create executable version of the script
        with open(overlay_src, "r") as src_file:
            content = src_file.read()
        
        with open(overlay_dest, "w") as dest_file:
            dest_file.write("#!/usr/bin/env python3\n" + content)
        
        os.chmod(overlay_dest, 0o755)
        
        print(f"App bundle created successfully at: {app_path}")
        return True
    except Exception as e:
        print(f"Error creating app bundle: {e}")
        return False

def create_dmg():
    """Create a DMG installer"""
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("Error: DMG creation is only supported on macOS.")
        return False
    
    # Check if app bundle exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "StealthAI.app")
    
    if not os.path.exists(app_path):
        print("Error: StealthAI.app not found. Create the app bundle first.")
        return False
    
    try:
        print("Creating DMG installer...")
        
        # Define DMG name
        dmg_name = "StealthAI-Installer.dmg"
        dmg_path = os.path.join(current_dir, dmg_name)
        
        # Remove existing DMG if it exists
        if os.path.exists(dmg_path):
            os.remove(dmg_path)
        
        # Create a temporary folder for the DMG contents
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the app to the temp directory
            temp_app_path = os.path.join(temp_dir, "StealthAI.app")
            shutil.copytree(app_path, temp_app_path)
            
            # Create Applications symlink
            os.symlink("/Applications", os.path.join(temp_dir, "Applications"))
            
            # Create DMG using hdiutil
            subprocess.run([
                "hdiutil", "create",
                "-volname", "StealthAI",
                "-srcfolder", temp_dir,
                "-ov", "-format", "UDZO",
                dmg_path
            ], check=True)
        
        print(f"DMG installer created successfully at: {dmg_path}")
        return True
    except Exception as e:
        print(f"Error creating DMG: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("StealthAI App Creator")
    print("=" * 60)
    
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("Warning: This script is designed for macOS.")
        print(f"Detected platform: {platform.system()}")
        print("Some features may not work correctly.")
    
    # Check dependencies
    print("\nChecking dependencies...")
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print("Some dependencies are missing.")
        install = input("Install missing dependencies? (y/n): ").lower()
        
        if install == 'y':
            if not install_dependencies(missing):
                print("Failed to install dependencies. Exiting.")
                return 1
        else:
            print("Cannot continue without required dependencies. Exiting.")
            return 1
    
    # Check OpenAI API key
    check_api_key()
    
    # Create app bundle
    print("\nCreating macOS application...")
    if not create_app_bundle():
        print("Failed to create app bundle. Exiting.")
        return 1
    
    # Create DMG
    print("\nCreating DMG installer...")
    create_dmg_success = create_dmg()
    
    # Print final instructions
    print("\n" + "=" * 60)
    print("Build Complete!")
    print("=" * 60)
    
    print("\nYou can now run the application in one of these ways:")
    print("1. Double-click StealthAI.app in Finder")
    print("2. Run: open StealthAI.app")
    
    if create_dmg_success:
        print("\nTo distribute to others:")
        print("- Share the StealthAI-Installer.dmg file")
        print("- Users can mount the DMG and drag StealthAI.app to their Applications folder")
    
    print("\nRequired Permissions:")
    print("- When first launching, you may need to right-click the app and select 'Open'")
    print("- Grant Accessibility permissions when prompted (for keyboard shortcuts)")
    print("- Grant Screen Recording permissions when prompted (for screen capture)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())