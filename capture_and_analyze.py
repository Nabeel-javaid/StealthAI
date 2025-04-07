"""
Screen Capture and Analysis Tool for macOS

This application captures your screen and sends it to OpenAI for analysis.
It provides an easy-to-use interface for getting AI insights about anything on your screen.
"""
import os
import sys
import time
import logging
import argparse
import platform
from datetime import datetime

# Import our modules
from screen_capture import ScreenCapture
from ai_assistant import AIAssistant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CaptureAndAnalyze")

class CaptureAnalyzer:
    """
    Main application class for screen capture and analysis
    """
    
    def __init__(self):
        """Initialize the application"""
        # Check if we're on macOS
        if platform.system() != "Darwin":
            logger.warning("This tool is optimized for macOS. Some features may not work on other platforms.")
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.ai_assistant = AIAssistant()
        
        # Check OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            logger.error("Please set the OPENAI_API_KEY environment variable")
            logger.error("Example: export OPENAI_API_KEY=your_api_key_here")
            sys.exit(1)
    
    def capture_and_analyze(self, custom_prompt=None):
        """
        Capture the screen and analyze it with OpenAI
        
        Args:
            custom_prompt (str, optional): Custom prompt for analysis
        
        Returns:
            str: Analysis result
        """
        logger.info("Capturing screen...")
        screenshot_path = self.screen_capture.capture_screen()
        
        if not screenshot_path:
            return "Failed to capture screen. Please make sure you have granted screen recording permissions."
        
        logger.info(f"Screen captured to: {screenshot_path}")
        logger.info("Analyzing with OpenAI...")
        
        # Default prompt if none provided
        if not custom_prompt:
            custom_prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
        
        # Get the base64 encoded image
        base64_image = self.screen_capture.encode_image(screenshot_path)
        if not base64_image:
            return "Failed to encode screenshot for analysis."
        
        # Send to OpenAI for analysis
        result = self.ai_assistant.analyze_image(base64_image, custom_prompt)
        
        # Clean up the temporary file
        self.screen_capture.clean_up()
        
        return result

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Capture and analyze your screen with AI")
    parser.add_argument("--prompt", type=str, help="Custom prompt for analysis", default=None)
    args = parser.parse_args()
    
    print("="*70)
    print("macOS Screen Capture and Analysis Tool")
    print("This tool will take a screenshot and analyze it with OpenAI")
    print("="*70)
    
    # Create the analyzer
    analyzer = CaptureAnalyzer()
    
    # Ask permission before capture
    print("This tool needs to capture your screen to analyze it.")
    confirmation = input("Do you want to continue? (y/n): ").lower()
    
    if confirmation != 'y':
        print("Operation cancelled by user.")
        sys.exit(0)
    
    # Custom prompt?
    if not args.prompt:
        print("\nYou can provide a custom prompt for the AI analysis.")
        print("For example: 'Explain the code in this screenshot' or 'Debug the error message shown'")
        custom_prompt = input("Custom prompt (or press Enter for default): ")
        if not custom_prompt.strip():
            custom_prompt = None
    else:
        custom_prompt = args.prompt
    
    # Capture and analyze
    print("\nCapturing screen in 3 seconds...", end="", flush=True)
    for i in range(3, 0, -1):
        time.sleep(1)
        print(f" {i}...", end="", flush=True)
    print(" Now!")
    
    # Get the result
    result = analyzer.capture_and_analyze(custom_prompt)
    
    # Print the result
    print("\n" + "="*70)
    print("ANALYSIS RESULT:")
    print("="*70)
    print(result)
    print("="*70)
    
    # Save result to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"screen_analysis_{timestamp}.txt"
    
    with open(result_file, "w") as f:
        f.write(result)
    
    print(f"\nAnalysis also saved to: {result_file}")
    print("\nThank you for using the Screen Capture and Analysis Tool!")

if __name__ == "__main__":
    main()