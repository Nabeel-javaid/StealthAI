# StealthAI: Discreet AI Coding Assistant for macOS

StealthAI is a specialized AI coding assistant that remains invisible during screen sharing sessions (Zoom, Teams, etc.), designed exclusively for macOS. It helps developers during coding interviews, technical assessments, and pair programming sessions by providing AI assistance that only you can see.

![StealthAI Banner](generated-icon.png)

## Key Features

- **Invisible During Screen Sharing**: Automatically detects screen sharing in macOS and becomes invisible to others
- **Instant AI Assistance**: Get coding help, problem-solving tips, and macOS development advice
- **Keyboard Shortcut Activation**: Press ⌘+⌥+C (Command+Option+C) to show/hide the assistant window
- **macOS-Optimized**: Built specifically for Apple platforms with native macOS APIs
- **Code Analysis**: Submit your code for instant analysis, suggestions, and improvements
- **Swift & Objective-C Expert**: Gets specialized assistance for Apple platform development

## Requirements

- macOS 10.14 (Mojave) or newer
- Python 3.7+
- OpenAI API key
- macOS permissions:
  - Accessibility (for keyboard shortcuts)
  - Screen Recording (optional, for enhanced screen sharing detection)

## Installation

1. Clone this repository
2. Run the setup script:
   ```bash
   ./run.sh
   ```
3. Follow the prompts to install dependencies and set up your API key

### Required Python Packages

- openai
- psutil
- pynput
- PyQt5 (for GUI)
- pyobjc (for macOS integration)

## Usage

### Running the Application

Use our convenient script to run the application:

```bash
./run.sh
```

Choose from multiple launch modes:
1. **Standard Mode**: Activates with keyboard shortcut (⌘+⌥+C)
2. **Debug Mode**: Shows window immediately for testing
3. **CLI Fallback Mode**: Text-based interface when GUI isn't available
4. **Create macOS App**: Bundles the application as a native macOS app

### Creating a macOS App Bundle

For the best experience, create a standalone macOS application:

1. Run the bundling script:
   ```bash
   python create_macos_app.py
   ```
   
2. The app will be created in the current directory as `StealthAI.app`

3. Move it to your Applications folder (optional):
   ```bash
   mv StealthAI.app /Applications/
   ```

### Granting Required Permissions

1. **Accessibility Permissions**:
   - Required for keyboard shortcuts to work
   - Go to System Preferences > Security & Privacy > Privacy > Accessibility
   - Add Terminal or StealthAI.app to the list of allowed apps

2. **Screen Recording Permissions** (optional but recommended):
   - Enhances screen sharing detection
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add Terminal or StealthAI.app to the list of allowed apps

## Keyboard Shortcuts

- **⌘+⌥+C** (Command+Option+C): Show/hide the assistant window

## Troubleshooting

### Keyboard Shortcuts Not Working

1. Ensure Terminal or StealthAI.app has Accessibility permissions
2. Try running in Debug Mode to verify the application works
3. Check if the pynput package is installed correctly

### Can't Detect Screen Sharing

1. Grant Screen Recording permissions to Terminal or StealthAI.app
2. The app will still work without this permission but may not auto-hide during sharing

### API Key Issues

1. Make sure your OpenAI API key is correctly set in your environment
2. You can add it to your shell profile (~/.zshrc or ~/.bash_profile):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. Or set it temporarily for the current session:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### App Not Working

1. Run the test scripts to diagnose issues:
   ```bash
   python test_api.py     # Test API connectivity
   python test_keyboard.py  # Test keyboard shortcuts
   ```
2. Try the CLI Fallback Mode if GUI isn't working:
   ```bash
   python fallback_mode.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses OpenAI API for AI assistance
- Built with PyQt5 for the GUI
- Uses pyobjc for macOS integration