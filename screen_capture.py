"""
Screen capture module for StealthAI
Captures screen content and sends it to OpenAI for analysis
"""
import os
import base64
import logging
import platform
import tempfile
import subprocess
from datetime import datetime

# Import AI Assistant for API communication
from ai_assistant import AIAssistant

logger = logging.getLogger(__name__)

class ScreenCapture:
    """
    Captures screenshots and processes them for AI analysis
    """
    
    def __init__(self):
        """Initialize screen capture module"""
        self.is_macos = platform.system() == "Darwin"
        self.ai_assistant = AIAssistant()
        self.last_capture_path = None
    
    def capture_screen(self):
        """
        Capture the current screen
        
        Returns:
            str: Path to saved screenshot
        """
        try:
            # Create temp file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            screenshot_path = os.path.join(temp_dir, f"screenshot_{timestamp}.png")
            
            if self.is_macos:
                # Use native macOS screencapture tool
                subprocess.run(
                    ["screencapture", "-x", screenshot_path],
                    check=True
                )
                logger.info(f"Screen captured to {screenshot_path}")
            else:
                # For non-macOS platforms, use other libraries
                raise NotImplementedError("Screen capture not implemented for this platform")
            
            # Store path for later use
            self.last_capture_path = screenshot_path
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error capturing screen: {str(e)}")
            return None
    
    def encode_image(self, image_path):
        """
        Encode image as base64 for API submission
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Base64 encoded image
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return None
    
    def analyze_screen(self, prompt=None):
        """
        Analyze current screen with OpenAI
        
        Args:
            prompt (str, optional): Additional instructions for analysis
            
        Returns:
            str: AI analysis of screen content
        """
        try:
            # Capture screen if not already captured
            if not self.last_capture_path or not os.path.exists(self.last_capture_path):
                screenshot_path = self.capture_screen()
                if not screenshot_path:
                    return "Failed to capture screen"
            else:
                screenshot_path = self.last_capture_path
            
            # Encode image
            base64_image = self.encode_image(screenshot_path)
            if not base64_image:
                return "Failed to encode image"
            
            # Default prompt if none provided
            if not prompt:
                prompt = "Analyze this screenshot and describe what you see. If there's code, explain what it does."
            
            # Get analysis from OpenAI through our AI assistant
            response = self.ai_assistant.analyze_image(base64_image, prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing screen: {str(e)}")
            return f"Error analyzing screen: {str(e)}"
    
    def clean_up(self):
        """Remove temporary screenshots"""
        try:
            if self.last_capture_path and os.path.exists(self.last_capture_path):
                os.remove(self.last_capture_path)
                logger.info(f"Deleted screenshot: {self.last_capture_path}")
                self.last_capture_path = None
        except Exception as e:
            logger.error(f"Error cleaning up screenshots: {str(e)}")