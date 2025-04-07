# Discreet AI Coding Assistant

A discreet desktop application that provides invisible AI coding assistance during screen sharing sessions, designed primarily for Windows but with cross-platform support.

## Overview

This application is designed for educational purposes to demonstrate potential limitations in screen sharing software. It allows users to get AI-powered coding assistance during screen sharing sessions without the assistance being visible to other participants.

## Features

- Background operation during screen sharing (invisible to viewers)
- Keyboard shortcut activation (default: Ctrl+Shift+A)
- Input mechanism for coding problems and questions
- AI-powered responses visible only to the user
- Focus on coding interview assistance
- Windows OS compatibility with enhanced invisibility features
- Cross-platform support with fallback mechanisms for Linux and macOS
- CLI mode for development and testing

## Requirements

- Windows operating system (for full functionality)
- Python 3.8 or higher
- OpenAI API key
- Dependencies: PyQt5/PySide2, pynput, openai

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install PyQt5 pynput openai
   ```
   
   For Windows, additional dependencies are needed:
   ```
   pip install psutil pywin32
   ```
   
3. Set your OpenAI API key as an environment variable:
   - Windows:
     ```
     setx OPENAI_API_KEY "your-api-key-here"
     ```
   - Linux/macOS:
     ```
     export OPENAI_API_KEY="your-api-key-here"
     ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. When in a screen sharing session, press Ctrl+Shift+A (default shortcut) to toggle the assistant window.

3. Enter your coding problem or paste interview question text.

4. Click "Get Help" to receive AI-powered assistance.

5. The window will automatically adjust its transparency when screen sharing is detected.

## Development Mode

When running on non-Windows platforms, the application will display a "Development Mode" checkbox that allows simulating screen sharing for testing the invisibility features.

## CLI Mode

If GUI libraries (PyQt5/PySide2) are not available, the application will run in CLI mode, which allows testing the AI assistance functionality without the GUI.

## Configuration

The application creates a configuration file at `~/.coding_assistant_config.json` with the following default settings:

- Activation shortcut: Ctrl+Shift+A
- Opacity: 0.9
- Font size: 12
- Default programming language: Python
- Theme: dark

You can manually edit this file to change these settings.

## Disclaimer

This tool is for educational purposes only. The ability to display content that is invisible during screen sharing could potentially be misused. Always use this tool ethically and responsibly, respecting privacy and academic integrity policies.

## License

MIT