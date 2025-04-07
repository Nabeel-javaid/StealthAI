#!/usr/bin/env python3
"""
Script to create a macOS .app bundle for the StealthAI Coding Assistant
This makes the application feel more native and avoids Terminal issues
"""
import os
import sys
import shutil
import subprocess
import platform

def main():
    """Create a macOS .app bundle for StealthAI"""
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        print(f"Detected platform: {platform.system()}")
        return 1
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Define app bundle structure
    app_name = "StealthAI.app"
    app_path = os.path.join(current_dir, app_name)
    
    # Create app bundle directories
    os.makedirs(f"{app_path}/Contents/MacOS", exist_ok=True)
    os.makedirs(f"{app_path}/Contents/Resources", exist_ok=True)
    
    # Create executable launcher script
    launcher_path = os.path.join(app_path, "Contents", "MacOS", "StealthAI")
    with open(launcher_path, "w") as f:
        f.write("""#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../../.."
/usr/bin/env pythonw run_macos_app.py
""")
    
    # Make the launcher executable
    os.chmod(launcher_path, 0o755)
    
    # Create Info.plist
    info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
    with open(info_plist_path, "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StealthAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.StealthAI</string>
    <key>CFBundleName</key>
    <string>StealthAI</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>NSAppleEventsUsageDescription</key>
    <string>StealthAI needs to control system events to detect screen sharing and stay invisible during screen sharing sessions.</string>
    <key>NSScreenCaptureUsageDescription</key>
    <string>StealthAI needs access to screen recording for detecting when screen sharing is active.</string>
</dict>
</plist>
""")
    
    # Copy the app icon if it exists
    icon_source = os.path.join(current_dir, "generated-icon.png")
    if os.path.exists(icon_source):
        icon_dest = os.path.join(app_path, "Contents", "Resources", "AppIcon.icns")
        # In a real implementation, we'd convert PNG to ICNS
        # For simplicity, we're just copying the PNG
        shutil.copy(icon_source, icon_dest.replace(".icns", ".png"))
        print(f"Copied app icon to {icon_dest}")
    
    print(f"Created macOS app bundle at: {app_path}")
    print("\nTo run the application:")
    print(f"1. Open Finder and navigate to {current_dir}")
    print(f"2. Double-click on {app_name}")
    print("\nNote: On first run, you'll need to grant permissions:")
    print("- Right-click the app and select 'Open' to bypass Gatekeeper")
    print("- Grant Accessibility and Screen Recording permissions when prompted")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())