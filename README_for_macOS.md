# StealthAI for macOS

A stealth screen capture and analysis tool for coding interviews and tests.

## Setup Instructions

### Option 1: Terminal-based solution (Most reliable)

For the most reliable solution that works on any macOS, use the terminal-based utility:

1. **Install Python dependencies**
   ```bash
   pip install openai
   ```

2. **Set your OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   
   For persistent access, add this to your `.zshrc` or `.bash_profile`:
   ```bash
   echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Run the simple capture utility**
   ```bash
   python simpler_capture.py
   ```

### Option 2: GUI-based solution (Experimental)

The GUI solution may have issues on some macOS versions:

1. **Install dependencies**
   ```bash
   pip install PyQt5 openai pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz pynput
   ```

2. **Run the simplified testing overlay**
   ```bash
   python super_simple_overlay.py
   ```

3. **If that works, try the stealth overlay**
   ```bash
   python stealth_overlay.py
   ```

## Important macOS Permissions

You'll need to grant these permissions in System Preferences:

1. **Accessibility permissions**
   - Go to System Preferences > Security & Privacy > Privacy > Accessibility
   - Add Terminal to the list
   - Enable it with the checkbox

2. **Screen Recording permissions**
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add Terminal to the list
   - Enable it with the checkbox

3. **Full Disk Access (optional)**
   - Might be needed if you encounter permission errors

## Using the Terminal-based Tool

1. Run `python simpler_capture.py`
2. Select option 1 to capture with default prompt or option 2 for custom prompt
3. The tool will count down, take a screenshot, and send it to OpenAI for analysis
4. Results will be displayed in the terminal and saved to a text file

## How to Use During Interviews

1. Start the tool before your interview/test begins
2. When you encounter a coding problem or question:
   - For the terminal tool: Just run the capture when needed
   - For the GUI tool: Press Command+Option+C to show the overlay, then click "Capture Screen & Analyze"
3. The AI will analyze the problem and provide a solution
4. The window remains hidden from screen sharing tools (with the full stealth overlay)

## Troubleshooting

- **Terminal-based tool is always the fallback option** if GUI tools don't work
- If GUI freezes, force quit and use the terminal version
- If you get permission errors, check System Preferences
- For OpenAI API errors, verify your API key is set correctly