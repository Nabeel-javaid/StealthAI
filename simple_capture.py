"""
Simple Screen Capture and Analysis Tool for macOS

This application captures your screen and sends it to OpenAI for analysis.
It provides a simple console interface for getting AI insights about anything on your screen.
"""
import os
import sys
import time
import logging
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
logger = logging.getLogger("SimpleCapture")

def main():
    """Main entry point for the application"""
    print("\n" + "="*70)
    print("macOS Screen Capture and Analysis Tool")
    print("="*70)
    
    # Check platform
    if platform.system() != "Darwin":
        print("⚠️  Warning: This tool is optimized for macOS.")
        print("Some features may not work on other platforms.")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API key not found in environment variables.")
        print("Please set the OPENAI_API_KEY environment variable.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Initialize components
    screen_capture = ScreenCapture()
    ai_assistant = AIAssistant()
    
    # Main menu loop
    while True:
        print("\nMain Menu:")
        print("1. Capture screen and analyze")
        print("2. Capture with custom prompt")
        print("3. Show example prompts")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # Default capture and analysis
            prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
            capture_and_analyze(screen_capture, ai_assistant, prompt)
            
        elif choice == '2':
            # Custom prompt
            print("\nEnter your custom prompt for analysis:")
            print("Examples: 'Explain the code in this screenshot', 'Debug the error message'")
            custom_prompt = input("> ").strip()
            if custom_prompt:
                capture_and_analyze(screen_capture, ai_assistant, custom_prompt)
            else:
                print("No prompt entered. Using default prompt.")
                prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
                capture_and_analyze(screen_capture, ai_assistant, prompt)
                
        elif choice == '3':
            # Show example prompts
            print("\nExample prompts you can use:")
            print("- 'Analyze this code and explain what it does'")
            print("- 'Debug the error message in this screenshot'")
            print("- 'Explain the UI elements in this application'")
            print("- 'Transcribe any text visible in this screenshot'")
            print("- 'Analyze this chart or graph and explain its meaning'")
            print("- 'Explain what's happening in this Terminal output'")
            print("- 'Help me understand the documentation shown in the screenshot'")
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            # Exit
            print("\nThank you for using the Screen Capture and Analysis Tool!")
            break
            
        else:
            print("\nInvalid choice. Please enter a number from 1 to 4.")

def capture_and_analyze(screen_capture, ai_assistant, prompt):
    """
    Capture the screen and analyze it with OpenAI
    
    Args:
        screen_capture (ScreenCapture): Screen capture instance
        ai_assistant (AIAssistant): AI assistant instance
        prompt (str): Prompt for analysis
    """
    # Permission check
    print("\n⚠️  This tool needs to capture your screen to analyze it.")
    print("On macOS, you need to grant screen recording permission in:")
    print("System Preferences > Security & Privacy > Privacy > Screen Recording")
    
    confirmation = input("\nDo you want to continue? (y/n): ").lower()
    if confirmation != 'y':
        print("Operation cancelled by user.")
        return
    
    # Countdown
    print("\nCapturing screen in 3 seconds...", end="", flush=True)
    for i in range(3, 0, -1):
        time.sleep(1)
        print(f" {i}...", end="", flush=True)
    print(" Now!")
    
    # Capture screen
    logger.info("Capturing screen")
    screenshot_path = screen_capture.capture_screen()
    
    if not screenshot_path:
        print("\n❌ Failed to capture screen.")
        print("Please make sure you have granted screen recording permissions.")
        return
    
    logger.info(f"Screen captured to: {screenshot_path}")
    
    # Encode image
    logger.info("Encoding image")
    base64_image = screen_capture.encode_image(screenshot_path)
    
    if not base64_image:
        print("\n❌ Failed to encode screenshot for analysis.")
        return
    
    # Analyze with OpenAI
    print("\n🔍 Analyzing screenshot with OpenAI...")
    print("This may take a moment...")
    
    try:
        result = ai_assistant.analyze_image(base64_image, prompt)
        
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
        
        print(f"\n✅ Analysis saved to: {result_file}")
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        print(f"\n❌ Error analyzing image: {str(e)}")
    
    # Clean up
    screen_capture.clean_up()

if __name__ == "__main__":
    main()