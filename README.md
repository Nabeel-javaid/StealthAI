# Discreet AI Coding Assistant for macOS

A discreet macOS application that provides invisible AI coding assistance during screen sharing sessions, optimized specifically for macOS.

## Overview

This application is designed for educational purposes to help during coding interviews on macOS. It allows you to get AI-powered coding assistance during screen sharing sessions without the assistance being visible to other participants.

## Features

- Background operation during screen sharing (completely invisible to viewers)
- Keyboard shortcut activation (default: Cmd+Option+C)
- AI-powered responses visible only to you
- Specialized coding interview assistance
- macOS-optimized screen sharing detection for Zoom, Teams, and other applications
- Advanced macOS-specific invisibility techniques
- Special macOS development advice and API guidance

## Requirements

- macOS 10.14 (Mojave) or higher
- Python 3.8 or higher
- OpenAI API key
- Dependencies: PyQt5, pynput, openai, psutil, pyobjc

## Installation and Running Instructions

### macOS Installation

1. Clone this repository to your Mac
2. Create a Python virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   # Core dependencies
   pip install PyQt5 pynput openai psutil
   
   # macOS specific dependencies 
   pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
   ```
4. Set your OpenAI API key:
   - As an environment variable: `export OPENAI_API_KEY="your-api-key"`
   - Or create a `.env` file with the content: `OPENAI_API_KEY=your-api-key`

### Running on macOS

#### Option 1: Create a macOS App (Recommended)
This avoids Terminal permission issues and provides a better experience:

1. Run the app creation script:
   ```bash
   python create_macos_app.py
   ```
2. Open the created `StealthAI.app` by right-clicking and selecting "Open"
3. Grant permissions when prompted
4. Use Cmd+Option+C to toggle the assistant window

#### Option 2: Run directly 
For regular use:
```bash
# Run with standard launcher
python run_macos_app.py
```

For development/debugging:
```bash
# Run directly
python main.py
```

### Using the App
1. Use the keyboard shortcut Cmd+Option+C to toggle the assistant window
2. Enter your coding question or paste your code
3. Click "Get Help" or "macOS Tips" to get AI assistance
4. The window will automatically become invisible during screen sharing

## macOS-Specific Features

- Window sharing prevention using NSWindowSharingNone and advanced macOS APIs
- Invisible window layer configuration using Cocoa and Quartz frameworks
- Special "macOS Tips" feature for Apple platform development advice
- Comprehensive support for Swift, Objective-C, and Apple frameworks
- Deep integration with macOS window management and screen capture detection
- Advanced detection for all popular screen sharing applications on macOS:
  - Zoom, Microsoft Teams, Slack, Discord
  - Webex, Google Meet, BlueJeans
  - Built-in macOS Screen Sharing
  - All major browsers (Safari, Chrome, Firefox)
- Custom macOS-specific keyboard shortcuts using Cmd+Option instead of Ctrl+Alt
- Designed for macOS accessibility and user experience guidelines
- macOS dark mode compatibility and automatic appearance switching

## Required Permissions

- Accessibility permissions (for keyboard shortcuts)
- Screen recording permissions (for detecting screen sharing)

## Configuration

Edit `~/.coding_assistant_config.json` to customize:
- Keyboard shortcut (default: Cmd+Option+C)
- Window opacity
- Default programming language 
- UI theme

## Disclaimer

This tool is for educational purposes only. It demonstrates techniques that allow content to remain invisible during screen sharing. Always use ethically and responsibly, respecting privacy and academic integrity policies.

## License

MIT
