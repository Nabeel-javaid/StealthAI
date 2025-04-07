# Installation Guide for StealthAI

This document provides detailed instructions for setting up the StealthAI Coding Assistant on macOS.

## Prerequisites

- macOS (10.14 Mojave or later recommended)
- Python 3.8 or later
- OpenAI API key

## Required macOS Permissions

For full functionality, you need to grant the following permissions:

1. **Accessibility Permissions** (for keyboard shortcuts):
   - Open System Preferences > Security & Privacy > Privacy > Accessibility
   - Click the lock icon to make changes
   - Add Terminal.app (or your Python IDE) to the list
   - Ensure the checkbox next to the application is checked

2. **Screen Recording Permissions** (for screen capture features):
   - Open System Preferences > Security & Privacy > Privacy > Screen Recording
   - Click the lock icon to make changes
   - Add Terminal.app (or your Python IDE) to the list
   - Ensure the checkbox next to the application is checked

**Note:** You may need to restart your Terminal or IDE after granting these permissions.

## Installation Steps

1. **Install Required Python Packages**

   ```bash
   # Dependencies for the main application
   pip install openai>=1.0.0 pynput>=1.7.6 psutil>=5.9.0
   
   # macOS-specific dependencies
   pip install PyObjC>=9.0.1
   
   # Optional: GUI support (for capture_gui.py)
   pip install PyQt5>=5.15.0
   ```

2. **Set Up Your OpenAI API Key**

   You need to set your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

   For persistent configuration, add this to your `.zshrc` or `.bash_profile`:

   ```bash
   echo 'export OPENAI_API_KEY=your_api_key_here' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Create a macOS App Bundle (Optional)**

   For a more native experience, you can create a macOS app bundle:

   ```bash
   python create_macos_app.py
   ```

   This will create a `StealthAI.app` that you can move to your Applications folder.

## Verification

To verify your installation is working correctly:

1. **Test API Connection**

   ```bash
   python test_api.py
   ```

2. **Test Keyboard Shortcuts**

   ```bash
   python test_keyboard.py
   ```

3. **Test Screen Capture**

   ```bash
   python simple_capture.py
   ```

## Troubleshooting

### Common Issues and Solutions

1. **"No module named 'openai'"**
   - Solution: Run `pip install openai>=1.0.0`

2. **Keyboard shortcuts not working**
   - Solution: Check accessibility permissions in System Preferences

3. **Screen capture showing blank or black screen**
   - Solution: Check screen recording permissions in System Preferences
   - Try running Terminal with elevated permissions

4. **OpenAI API errors**
   - Verify your API key is correct and has sufficient credits
   - Check your internet connection

5. **"No module named 'Quartz'" or similar PyObjC errors**
   - Solution: Run `pip install PyObjC>=9.0.1`

6. **GUI not appearing**
   - For PyQt5 issues: Run `pip install PyQt5>=5.15.0`
   - Try running in debug mode: `python debug_mode.py`

### Getting Help

If you continue to experience issues, try the following:

1. Check the application logs in the `assistant.log` file
2. Run in debug mode: `python debug_mode.py`
3. Try the fallback CLI mode: `python fallback_mode.py`