# StealthAI Installation Guide

This guide provides detailed instructions for installing and setting up StealthAI, a screen capture and analysis tool that works invisibly during interviews and exams.

## Prerequisites

- macOS 10.15 or newer
- Python 3.7+
- OpenAI API key

## Installation Options

### Option 1: Automated Installation (Recommended)

1. Download the latest release from the GitHub repository
2. Run the installation script:
   ```bash
   chmod +x invisibility_setup.sh
   ./invisibility_setup.sh
   ```
3. The script will:
   - Install required dependencies
   - Set up your OpenAI API key
   - Install the application as a background service
   - Create a hidden folder for results
   - Provide usage instructions

### Option 2: Manual Installation

1. Install required Python packages:
   ```bash
   pip install openai pynput
   ```

2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   
   For persistent access, add this to your shell profile:
   ```bash
   echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. Copy the application files to a location of your choice:
   ```bash
   mkdir -p ~/Library/Application\ Support/StealthAI
   cp hidden_capture.py ~/Library/Application\ Support/StealthAI/
   chmod +x ~/Library/Application\ Support/StealthAI/hidden_capture.py
   ```

4. Set up autostart (optional):
   Create a launch agent at `~/Library/LaunchAgents/com.stealthai.capture.plist` with the following content:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.stealthai.capture</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>~/Library/Application Support/StealthAI/hidden_capture.py</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <false/>
       <key>EnvironmentVariables</key>
       <dict>
           <key>OPENAI_API_KEY</key>
           <string>your_api_key_here</string>
       </dict>
   </dict>
   </plist>
   ```

5. Load the launch agent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.stealthai.capture.plist
   ```

## Required macOS Permissions

StealthAI requires the following permissions:

1. **Screen Recording**
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add Terminal or the app you're using to run StealthAI

2. **Accessibility**
   - Go to System Preferences > Security & Privacy > Privacy > Accessibility
   - Add Terminal or the app you're using to run StealthAI

You will be prompted to grant these permissions the first time you run the application.

## Usage

### Using the Hidden Capture Tool (hidden_capture.py)

This tool runs invisibly in the background. Use these keyboard shortcuts:

- **Command+Shift+1**: Capture and analyze coding problems
- **Command+Shift+2**: Capture and analyze multiple choice questions
- **Command+Shift+3**: Capture and debug code

Results are saved to: `~/Documents/.interview_helper/`

### Using the Terminal Tool (simpler_capture.py)

If you prefer a terminal interface:

1. Run the tool:
   ```bash
   python3 simpler_capture.py
   ```

2. Select the analysis type:
   - Option 1: Coding Problem
   - Option 2: Multiple Choice
   - Option 3: Debug Code
   - Option 4: Custom Prompt

3. The tool will:
   - Count down before taking a screenshot
   - Send the screenshot to OpenAI for analysis
   - Display and save the results

Results are saved to: `~/Documents/AI_Analysis/`

### Using the Universal Capture Tool (universal_capture.py)

For analyzing existing images:

```bash
python3 universal_capture.py path/to/image.png
```

With custom prompt:
```bash
python3 universal_capture.py path/to/image.png --prompt "Analyze this coding problem"
```

## Viewing Results

- **Hidden Capture Tool**: Results are in `~/Documents/.interview_helper/`
- **Simple Capture Tool**: Results are in `~/Documents/AI_Analysis/`

Each result includes:
- The original screenshot
- A text file with the analysis
- An HTML file with formatted analysis and the image

## Troubleshooting

1. **Keyboard Shortcuts Not Working**
   - Make sure Accessibility permissions are granted
   - Check if there are conflicting system shortcuts

2. **Screen Capture Fails**
   - Verify Screen Recording permissions are granted
   - Try running the terminal tool to test basic functionality

3. **OpenAI API Errors**
   - Check that your API key is correctly set
   - Verify your OpenAI account has available credits

## Uninstalling

To completely remove StealthAI:

1. Unload the launch agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.stealthai.capture.plist
   ```

2. Remove the files:
   ```bash
   rm ~/Library/LaunchAgents/com.stealthai.capture.plist
   rm -rf ~/Library/Application\ Support/StealthAI
   rm -rf ~/Documents/.interview_helper
   rm -rf ~/Documents/AI_Analysis
   ```