#!/bin/bash
# This script demonstrates an alternative approach to creating a macOS app
# that doesn't rely on PyQt, which seems to be having issues.

echo "StealthAI Alternative Approach"
echo "============================="
echo ""

# Determine the right Python to use
PYTHON_PATH=$(which python3)
echo "Using Python at: $PYTHON_PATH"

# Create a temporary directory for our app bundle
TEMP_DIR=$(mktemp -d)
APP_DIR="$TEMP_DIR/StealthAI.app"
echo "Creating app bundle at: $APP_DIR"

# Create app bundle structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StealthAI</string>
    <key>CFBundleIdentifier</key>
    <string>com.stealthai.capture</string>
    <key>CFBundleName</key>
    <string>StealthAI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>NSScreenCaptureUsageDescription</key>
    <string>StealthAI needs to capture your screen to analyze coding problems.</string>
</dict>
</plist>
EOF

# Copy the app bundle to the current directory
APP_NAME="StealthAI.app"
rm -rf "./$APP_NAME"
cp -R "$APP_DIR" "./$APP_NAME"

echo "App bundle created at: $APP_NAME"
