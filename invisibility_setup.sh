#!/bin/bash
# Setup script for the invisible screen capture tool
# This script installs the necessary dependencies and sets up the tool to run automatically

echo "=========================================="
echo "   StealthAI - Invisible Capture Setup"
echo "=========================================="
echo

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script is for macOS only."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install openai pynput --quiet

# Check for OpenAI API key
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "OpenAI API key not found in environment."
    read -p "Enter your OpenAI API key: " API_KEY
    
    if [[ -z "$API_KEY" ]]; then
        echo "No API key provided. Exiting."
        exit 1
    fi
    
    # Save API key to shell profile
    if [[ -f "$HOME/.zshrc" ]]; then
        PROFILE="$HOME/.zshrc"
    else
        PROFILE="$HOME/.bash_profile"
    fi
    
    echo "export OPENAI_API_KEY='$API_KEY'" >> "$PROFILE"
    echo "API key added to $PROFILE"
    export OPENAI_API_KEY="$API_KEY"
else
    echo "OpenAI API key found in environment."
fi

# Create application directory
APP_DIR="$HOME/Library/Application Support/StealthAI"
mkdir -p "$APP_DIR"

# Copy the Python script to the app directory
cp hidden_capture.py "$APP_DIR/"
chmod +x "$APP_DIR/hidden_capture.py"

# Create a launch agent to run the tool at login
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
LAUNCH_AGENT_FILE="$LAUNCH_AGENT_DIR/com.stealthai.capture.plist"

mkdir -p "$LAUNCH_AGENT_DIR"

cat > "$LAUNCH_AGENT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stealthai.capture</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${APP_DIR}/hidden_capture.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>${OPENAI_API_KEY}</string>
    </dict>
</dict>
</plist>
EOF

# Load the launch agent
launchctl load "$LAUNCH_AGENT_FILE"

# Create a README file with usage instructions
README_FILE="$HOME/Documents/StealthAI_Instructions.txt"

cat > "$README_FILE" << EOF
StealthAI - Invisible Screen Capture Tool
=========================================

This tool runs invisibly in the background and captures your screen when you
press keyboard shortcuts. The captures are analyzed using OpenAI and saved
to your Documents folder.

Keyboard Shortcuts:
------------------
Command+Shift+1: Capture screen and analyze coding problems
Command+Shift+2: Capture screen and analyze multiple choice questions
Command+Shift+3: Capture screen and analyze code for debugging

Where to find results:
---------------------
Results are saved to: ~/Documents/.interview_helper/
(This is a hidden folder, to view it in Finder press Command+Shift+. to show hidden files)

Each capture creates 3 files:
- capture_[timestamp].png: The screenshot
- capture_[timestamp]_result.txt: The analysis text
- capture_[timestamp]_result.html: A formatted HTML version of the analysis

How to use during interviews:
----------------------------
1. The tool is already running in the background
2. When you encounter a difficult question, press the appropriate shortcut
3. You'll hear a subtle "tink" sound when the analysis is complete
4. After the interview, check the results folder to see the answers

To uninstall:
------------
Run this command in Terminal:
launchctl unload ~/Library/LaunchAgents/com.stealthai.capture.plist

EOF

echo
echo "StealthAI installed successfully!"
echo "Instructions saved to: $README_FILE"
echo
echo "Usage:"
echo "- Press Command+Shift+1 to analyze coding problems"
echo "- Press Command+Shift+2 to analyze multiple choice questions"
echo "- Press Command+Shift+3 to debug code"
echo
echo "Results will be saved to: ~/Documents/.interview_helper/"
echo
echo "To start using it right now, run:"
echo "python3 $APP_DIR/hidden_capture.py &"
