# StealthAI: Discreet macOS AI Coding Assistant

A discreet AI assistant application exclusively for macOS that remains invisible during screen sharing sessions. It analyzes coding problems, captures screen content, and provides AI-powered assistance without being detected by screen sharing tools.

## Features

- **Invisible Window**: Remains completely undetected during screen sharing in Zoom, Teams, and other applications
- **Keyboard Shortcuts**: Activate with simple keyboard shortcuts (Command+Option+C by default)
- **Code Analysis**: Get expert guidance on coding problems, algorithm optimization, and debugging
- **Screen Capture**: Analyze screenshots of code, UI, or any content with OpenAI's multimodal capabilities
- **macOS Integration**: Native macOS experience with system-level integration

## Installation Requirements

- macOS (any recent version)
- Python 3.8+
- OpenAI API key (required for all AI capabilities)

## Required Permissions

For this application to function properly, you need to grant:

1. **Accessibility Permissions**:
   - System Preferences (System Settings) > Security & Privacy > Privacy > Accessibility
   - Add Terminal (or your Python IDE) to the list

2. **Screen Recording Permissions** (for screen capture features):
   - System Preferences (System Settings) > Security & Privacy > Privacy > Screen Recording
   - Add Terminal (or your Python IDE) to the list

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Main Application

Start the stealth AI mode that activates on keyboard shortcut:

```bash
python main.py
```

### Screen Capture Tools

We provide multiple ways to capture and analyze your screen:

#### 1. Simple Console Interface

Use a simple menu-driven console interface:

```bash
python simple_capture.py
```

This provides an easy-to-use interface with options for:
- Quick screen analysis
- Custom prompts for specific tasks
- Example prompt suggestions

#### 2. Advanced Capture Tool

For more detailed analysis with custom prompts:

```bash
python capture_and_analyze.py
```

You can add custom prompts directly:

```bash
python capture_and_analyze.py --prompt "Debug the error message in this screenshot"
```

#### 3. GUI Interface (when available)

For a native macOS experience with a graphical interface:

```bash
python capture_gui.py
```

This requires PyQt5 to be installed and provides a full-featured GUI experience.

### Debug Mode

If you're having issues with keyboard shortcuts, run in debug mode to show the window immediately:

```bash
python debug_mode.py
```

### Fallback Mode

For environments where GUI isn't available:

```bash
python fallback_mode.py
```

## Troubleshooting

### Keyboard Shortcuts Not Working

1. Ensure you've granted accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility
2. Try using debug mode: `python debug_mode.py`
3. Check for conflicting system-wide keyboard shortcuts

### Screen Capture Not Working

1. Ensure you've granted screen recording permissions in System Preferences > Security & Privacy > Privacy > Screen Recording
2. Try restarting your Terminal or IDE after granting permissions
3. Verify your OpenAI API key is set correctly with: `echo $OPENAI_API_KEY`

### OpenAI API Issues

1. Ensure your API key is valid and has sufficient credits
2. Check your internet connection
3. Verify you're using a supported OpenAI model (gpt-4o is recommended)

## Customization

You can customize the keyboard shortcuts and other settings in `config.py`.