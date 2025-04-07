#!/usr/bin/env python3
"""
Hidden Screen Capture Tool for Interviews

This tool is designed to be completely invisible during screen sharing:
1. It runs as a background process with no visible window
2. Uses keyboard shortcuts to trigger screen capture without visible UI
3. Analyzes problems using OpenAI and saves results where they can be viewed later
4. Uses various techniques to avoid detection in screen sharing
"""
import os
import sys
import time
import base64
import tempfile
import logging
import threading
import subprocess
from datetime import datetime

# Configure logging to file instead of console (to avoid visibility)
log_dir = os.path.expanduser("~/Documents")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "hidden_capture.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import OpenAI silently
try:
    import openai
except ImportError:
    logger.error("OpenAI package not installed")
    sys.exit(1)

# Try to import keyboard listening library silently
try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    logger.error("pynput not installed")
    KEYBOARD_AVAILABLE = False

class HiddenCapture:
    """Hidden screen capture and analysis tool"""
    
    def __init__(self):
        """Initialize the hidden capture tool"""
        # Check for OpenAI API key
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not set")
            sys.exit(1)
            
        # Set up OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Create results directory (hidden in Documents)
        self.results_dir = os.path.expanduser("~/Documents/.interview_helper")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Set up keyboard listener
        if KEYBOARD_AVAILABLE:
            self._setup_keyboard_listener()
        
        # Flag to keep the program running
        self.running = True
        
        logger.info("Hidden capture initialized successfully")
    
    def _setup_keyboard_listener(self):
        """Set up keyboard shortcuts listener"""
        try:
            # Capture on Command+Shift+1
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            logger.info("Keyboard listener started")
        except Exception as e:
            logger.error(f"Failed to setup keyboard listener: {e}")
    
    def _on_key_press(self, key):
        """Handle keyboard shortcut presses"""
        try:
            # Check for Command+Shift+1 (capture with default prompt)
            if hasattr(key, 'vk') and key.vk == 49:  # '1' key
                modifiers = self._get_active_modifiers()
                if 'cmd' in modifiers and 'shift' in modifiers:
                    logger.info("Shortcut detected: Command+Shift+1")
                    threading.Thread(target=self.capture_and_analyze, args=(1,)).start()
            
            # Command+Shift+2 (capture with multiple choice prompt)
            elif hasattr(key, 'vk') and key.vk == 50:  # '2' key
                modifiers = self._get_active_modifiers()
                if 'cmd' in modifiers and 'shift' in modifiers:
                    logger.info("Shortcut detected: Command+Shift+2")
                    threading.Thread(target=self.capture_and_analyze, args=(2,)).start()
            
            # Command+Shift+3 (capture with debugging prompt)
            elif hasattr(key, 'vk') and key.vk == 51:  # '3' key
                modifiers = self._get_active_modifiers()
                if 'cmd' in modifiers and 'shift' in modifiers:
                    logger.info("Shortcut detected: Command+Shift+3")
                    threading.Thread(target=self.capture_and_analyze, args=(3,)).start()
                    
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _get_active_modifiers(self):
        """Get active modifier keys"""
        # This is a simplified version - a real implementation would track modifier key states
        return {'cmd', 'shift'}  # Assume modifiers are pressed for demo
    
    def capture_and_analyze(self, prompt_type=1):
        """Capture screen and analyze with OpenAI"""
        try:
            # Capture the screen silently
            screenshot_path = self._capture_screen()
            if not screenshot_path:
                logger.error("Screen capture failed")
                return
            
            # Choose prompt based on type
            prompt = self._get_prompt_for_type(prompt_type)
            
            # Analyze with OpenAI
            result = self._analyze_with_openai(screenshot_path, prompt)
            if not result:
                logger.error("Analysis failed")
                return
            
            # Save result to hidden file
            self._save_result(result, screenshot_path)
            
            # Play a subtle notification sound
            self._play_success_sound()
            
        except Exception as e:
            logger.error(f"Error in capture and analyze: {e}")
    
    def _capture_screen(self):
        """Capture screen silently using screencapture utility"""
        try:
            # Generate timestamp and paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            screenshot_path = os.path.join(self.results_dir, filename)
            
            # Use macOS screencapture utility with silent flag
            subprocess.run(
                ["screencapture", "-x", screenshot_path],
                check=True,
                capture_output=True  # Hide output
            )
            
            logger.info(f"Screen captured to: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return None
    
    def _get_prompt_for_type(self, prompt_type):
        """Get appropriate prompt based on type"""
        if prompt_type == 1:  # Coding problem
            return "Analyze this coding problem. Identify the task, provide a detailed step-by-step solution, and include working code with explanations."
        elif prompt_type == 2:  # Multiple choice
            return "Analyze this multiple choice question. Identify the correct answer and explain why it's correct and why the other options are incorrect."
        elif prompt_type == 3:  # Debugging
            return "Debug this code. Identify any errors, explain why they're happening, and provide fixed code."
        else:
            return "Analyze what's shown in this screenshot and provide detailed information."
    
    def _analyze_with_openai(self, image_path, prompt):
        """Analyze image with OpenAI Vision"""
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # The newest OpenAI model is "gpt-4o"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error analyzing with OpenAI: {e}")
            return None
    
    def _save_result(self, result, screenshot_path):
        """Save analysis result to file"""
        try:
            # Generate result filename based on screenshot name
            base_name = os.path.splitext(os.path.basename(screenshot_path))[0]
            result_filename = f"{base_name}_result.txt"
            result_path = os.path.join(self.results_dir, result_filename)
            
            # Save the result
            with open(result_path, "w") as f:
                f.write(result)
            
            logger.info(f"Result saved to: {result_path}")
            
            # Also create a HTML file that's easy to view
            html_path = os.path.join(self.results_dir, f"{base_name}_result.html")
            with open(html_path, "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Analysis Result</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .timestamp {{ color: #777; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Analysis Result</h1>
    <div class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    <pre>{result}</pre>
</body>
</html>
""")
            
        except Exception as e:
            logger.error(f"Error saving result: {e}")
    
    def _play_success_sound(self):
        """Play a subtle success sound as notification"""
        try:
            # Use macOS afplay for subtle notification
            subprocess.run(
                ["afplay", "/System/Library/Sounds/Tink.aiff"],
                check=False,
                capture_output=True  # Hide output
            )
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
    
    def run(self):
        """Run the hidden capture service"""
        logger.info("Hidden capture service running")
        logger.info("Use Command+Shift+1 for coding problems")
        logger.info("Use Command+Shift+2 for multiple choice questions")
        logger.info("Use Command+Shift+3 for debugging code")
        logger.info(f"Results will be saved to: {self.results_dir}")
        
        # Keep the program running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down hidden capture")
            self.running = False
            if KEYBOARD_AVAILABLE and hasattr(self, 'listener'):
                self.listener.stop()


def main():
    """Main function"""
    try:
        # Hide console window on Windows if we're on Windows
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # Start hidden capture
        capture = HiddenCapture()
        capture.run()
        
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())