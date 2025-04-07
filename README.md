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
2. Create a Python virtual environment (optional but recommended)
3. Install required dependencies:
   - Core: PyQt5, pynput, openai, psutil
   - macOS specific: pyobjc-core, pyobjc-framework-Cocoa, pyobjc-framework-Quartz
4. Set your OpenAI API key as an environment variable
5. Run the application with `python main.py`

### Running on macOS

1. Start the application with `python main.py`
2. Use the keyboard shortcut Cmd+Option+C to toggle the assistant window
3. Enter your coding question or paste your code
4. Click "Get Help" or "macOS Tips" to get AI assistance
5. The window will automatically become invisible during screen sharing

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
