#!/usr/bin/env python3
"""
Create macOS .app bundle and DMG installer for StealthAI Overlay

This script creates a standalone macOS application bundle (.app) and packages
it into a distributable DMG file that users can easily install on their Mac systems.
"""
import os
import sys
import shutil
import subprocess
import platform
import tempfile
import stat
from pathlib import Path

def create_app_bundle():
    """Create a macOS .app bundle for the application"""
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        print(f"Detected platform: {platform.system()}")
        return None
    
    print("Creating macOS application bundle...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Define app bundle structure
    app_name = "StealthAI.app"
    app_path = os.path.join(current_dir, app_name)
    
    # Remove existing app if it exists
    if os.path.exists(app_path):
        print(f"Removing existing app bundle: {app_path}")
        shutil.rmtree(app_path)
    
    # Create app bundle directories
    os.makedirs(f"{app_path}/Contents/MacOS", exist_ok=True)
    os.makedirs(f"{app_path}/Contents/Resources", exist_ok=True)
    os.makedirs(f"{app_path}/Contents/Frameworks", exist_ok=True)
    
    # Create executable launcher script
    launcher_path = os.path.join(app_path, "Contents", "MacOS", "StealthAI")
    print(f"Creating launcher script at: {launcher_path}")
    
    with open(launcher_path, "w") as f:
        f.write("""#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_ROOT="$DIR/../.."

# Launch using Python
cd "$APP_ROOT/Contents/Resources"
export PYTHONPATH="$APP_ROOT/Contents/Resources"
/usr/bin/env python3 stealth_overlay.py
""")
    
    # Make the launcher executable
    os.chmod(launcher_path, 0o755)
    
    # Create Info.plist
    info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
    print(f"Creating Info.plist at: {info_plist_path}")
    
    with open(info_plist_path, "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StealthAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.stealthai.overlay</string>
    <key>CFBundleName</key>
    <string>StealthAI</string>
    <key>CFBundleDisplayName</key>
    <string>StealthAI Overlay</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>NSAppleEventsUsageDescription</key>
    <string>StealthAI needs to control system events to detect screen sharing and stay invisible during screen sharing sessions.</string>
    <key>NSScreenCaptureUsageDescription</key>
    <string>StealthAI needs access to screen recording to analyze coding problems and provide assistance.</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
""")
    
    # Copy application files
    resources_dir = os.path.join(app_path, "Contents", "Resources")
    
    # Copy stealth_overlay.py
    print("Copying application files...")
    stealth_overlay_src = os.path.join(current_dir, "stealth_overlay.py")
    stealth_overlay_dest = os.path.join(resources_dir, "stealth_overlay.py")
    shutil.copy2(stealth_overlay_src, stealth_overlay_dest)
    
    # Create a simple script to set API key
    set_api_key_script = os.path.join(resources_dir, "set_api_key.py")
    with open(set_api_key_script, "w") as f:
        f.write("""#!/usr/bin/env python3
'''
Set OpenAI API Key for StealthAI
'''
import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

def main():
    '''Show dialog to set API key'''
    # Create and hide root window
    root = tk.Tk()
    root.withdraw()
    
    # Show API key input dialog
    api_key = simpledialog.askstring(
        "StealthAI - Set API Key", 
        "Enter your OpenAI API Key:",
        parent=root
    )
    
    if not api_key:
        messagebox.showinfo("Cancelled", "API key setup cancelled")
        return
    
    # Get user's home directory
    home_dir = os.path.expanduser("~")
    
    # Choose profile file based on shell
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        profile_file = os.path.join(home_dir, ".zshrc")
    else:
        profile_file = os.path.join(home_dir, ".bash_profile")
    
    # Check if key already exists
    try:
        with open(profile_file, "r") as f:
            content = f.read()
            if f"OPENAI_API_KEY={api_key}" in content:
                messagebox.showinfo("Success", f"API key already set in {profile_file}")
                return
    except FileNotFoundError:
        pass
    
    # Add key to profile file
    try:
        with open(profile_file, "a") as f:
            f.write(f"\\n# Added by StealthAI\\nexport OPENAI_API_KEY='{api_key}'\\n")
        
        messagebox.showinfo(
            "Success", 
            f"API key added to {profile_file}\\n\\nPlease restart your terminal or run:\\nsource {profile_file}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set API key: {str(e)}")

if __name__ == "__main__":
    main()
""")
    os.chmod(set_api_key_script, 0o755)
    
    # Create app icon
    icon_path = os.path.join(resources_dir, "AppIcon.png")
    create_icon(icon_path)
    
    print(f"Successfully created app bundle at: {app_path}")
    return app_path

def create_dmg(app_path):
    """Create a DMG installer for the application"""
    if not app_path or not os.path.exists(app_path):
        print("App bundle not found, cannot create DMG")
        return None
    
    print("Creating DMG installer...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Define DMG path
    dmg_name = "StealthAI-Installer.dmg"
    dmg_path = os.path.join(current_dir, dmg_name)
    
    # Remove existing DMG if it exists
    if os.path.exists(dmg_path):
        print(f"Removing existing DMG: {dmg_path}")
        os.remove(dmg_path)
    
    # Create temporary directory for DMG contents
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy app to temporary directory
        temp_app_path = os.path.join(temp_dir, os.path.basename(app_path))
        shutil.copytree(app_path, temp_app_path)
        
        # Create Applications symlink
        applications_link = os.path.join(temp_dir, "Applications")
        os.symlink("/Applications", applications_link)
        
        # Create README file
        readme_path = os.path.join(temp_dir, "README.txt")
        with open(readme_path, "w") as f:
            f.write("""StealthAI Overlay - Installation Instructions

1. Drag StealthAI.app to the Applications folder
2. Open StealthAI from Applications
3. Grant Accessibility and Screen Recording permissions when prompted
4. Press Command+Option+C to show/hide the overlay
5. Use the "Capture Screen & Analyze" button during interviews

Note: You will need an OpenAI API key to use the analysis features.
""")
        
        # Create DMG using hdiutil
        try:
            print(f"Creating DMG file: {dmg_path}")
            subprocess.run([
                "hdiutil", "create", "-volname", "StealthAI Installer",
                "-srcfolder", temp_dir, "-ov", "-format", "UDZO",
                dmg_path
            ], check=True)
            print(f"Successfully created DMG at: {dmg_path}")
            return dmg_path
        except subprocess.CalledProcessError as e:
            print(f"Error creating DMG: {e}")
            return None

def create_icon(output_path):
    """Create a simple app icon"""
    print(f"Creating app icon at: {output_path}")
    
    # This would typically involve creating a proper icon
    # For simplicity, we'll just create a basic PNG
    icon_data = """
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" fill="#4CAF50" rx="100" ry="100"/>
  <circle cx="256" cy="256" r="180" fill="#2E7D32"/>
  <path d="M160 352l60-100 60 70 60-120 80 150z" stroke="white" stroke-width="16" fill="none"/>
  <circle cx="256" cy="150" r="40" fill="white"/>
</svg>
"""
    
    # Save the SVG
    svg_path = output_path.replace(".png", ".svg")
    with open(svg_path, "w") as f:
        f.write(icon_data)
    
    # Try to convert SVG to PNG if possible
    try:
        subprocess.run([
            "convert", "-background", "none", svg_path, output_path
        ], check=True)
        os.remove(svg_path)  # Clean up SVG
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback - just copy the SVG
        shutil.copy2(svg_path, output_path)
        print("Note: ImageMagick not found, using SVG icon instead")

def main():
    """Create the app bundle and DMG installer"""
    if platform.system() != "Darwin":
        print("Error: This script is designed for macOS only.")
        print(f"Detected platform: {platform.system()}")
        return 1
    
    # Create the app bundle
    app_path = create_app_bundle()
    if not app_path:
        print("Error: Failed to create application bundle")
        return 1
    
    # Create the DMG installer
    dmg_path = create_dmg(app_path)
    if not dmg_path:
        print("Warning: Failed to create DMG installer")
        print("The app bundle is still available for testing")
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("=" * 50)
    
    print("\nTo test the application:")
    print(f"1. Open Finder and navigate to {os.path.dirname(os.path.realpath(__file__))}")
    print("2. Double-click on StealthAI.app")
    
    if dmg_path:
        print("\nTo distribute the application:")
        print(f"1. Share the DMG file: {os.path.basename(dmg_path)}")
        print("2. Users can mount the DMG and drag StealthAI.app to their Applications folder")
    
    print("\nNote: When first running the app, users must:")
    print("1. Right-click on StealthAI.app and select 'Open' (to bypass Gatekeeper)")
    print("2. Allow Accessibility permissions in System Preferences")
    print("3. Allow Screen Recording permissions in System Preferences")
    print("4. Set their OpenAI API key")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())