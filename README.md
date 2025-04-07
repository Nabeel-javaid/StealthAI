# Discreet AI Coding Assistant

A discreet desktop application that provides invisible AI coding assistance during screen sharing sessions, with optimized support for macOS, Windows, and cross-platform compatibility.

## Overview

This application is designed for educational purposes to demonstrate potential limitations in screen sharing software. It allows users to get AI-powered coding assistance during screen sharing sessions without the assistance being visible to other participants.

## Features

- Background operation during screen sharing (invisible to viewers)
- Keyboard shortcut activation (default: Ctrl+Alt+C)
- Input mechanism for coding problems and questions
- AI-powered responses visible only to the user
- Focus on coding interview assistance
- Enhanced screen sharing detection and invisibility for macOS and Windows
- Advanced invisibility using platform-specific techniques
- CLI mode for development and testing

## Requirements

- macOS, Windows, or Linux operating system
- Python 3.8 or higher
- OpenAI API key
- Dependencies: PyQt5/PySide2, pynput, openai

## Installation

### macOS Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install PyQt5 pynput openai psutil
   ```
   
   For enhanced macOS functionality:
   ```
   pip install pyobjc
   ```
   
3. Set your OpenAI API key as an environment variable:
   ```
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Windows Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install PyQt5 pynput openai psutil pywin32
   ```
   
3. Set your OpenAI API key as an environment variable:
   ```
   setx OPENAI_API_KEY "your-api-key-here"
   ```

### Linux Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install PyQt5 pynput openai psutil
   ```
   
3. Set your OpenAI API key as an environment variable:
   ```
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. When in a screen sharing session, press Ctrl+Alt+C (default shortcut) to toggle the assistant window.

3. Enter your coding problem or paste interview question text.

4. Click "Get Help" to receive AI-powered assistance.

5. The window will automatically adjust its transparency when screen sharing is detected.

## macOS Specific Instructions

### Screen Sharing Detection
The application will detect when you're sharing your screen in popular applications like Zoom, Microsoft Teams, and Discord. It automatically adjusts the visibility when screen sharing is detected.

### Invisibility Mode
On macOS, the application uses several techniques to remain invisible during screen sharing:

1. **Window Sharing Type**: Sets the window sharing type to NSWindowSharingNone
2. **Window Level**: Adjusts the window level to a layer that's typically not captured
3. **AppleScript Control**: Uses AppleScript to modify window properties

### macOS-Specific Coding Advice
The application includes a special feature for macOS users:

1. **Get macOS Tips**: Get macOS-specific advice for coding problems, optimized for Apple platforms
2. **Platform APIs**: Receive guidance on macOS-specific APIs and optimizations
3. **Objective-C/Swift Support**: Enhanced support for Apple's programming languages

### Permissions
For full functionality on macOS, you may need to:

1. Grant Accessibility permissions to Terminal/IDE in System Preferences > Security & Privacy > Privacy > Accessibility


### Troubleshooting
If the window is still visible during screen sharing:
- Try running the application with sudo (may require additional permissions)
- Verify that PyObjC is properly installed
- Use the Development Mode checkbox to test invisibility features

## Development Mode

When running on non-macOS platforms, the application will display a "Development Mode" checkbox that allows simulating screen sharing for testing the invisibility features.

## CLI Mode

If GUI libraries (PyQt5/PySide2) are not available, the application will run in CLI mode, which allows testing the AI assistance functionality without the GUI.

## Configuration

The application creates a configuration file at `~/.coding_assistant_config.json` with the following default settings:

- Activation shortcut: Ctrl+Alt+C
- Opacity: 0.9
- Font size: 12
- Default programming language: Python
- Theme: dark

You can manually edit this file to change these settings.

## Disclaimer

This tool is for educational purposes only. The ability to display content that is invisible during screen sharing could potentially be misused. Always use this tool ethically and responsibly, respecting privacy and academic integrity policies.

## License

MIT