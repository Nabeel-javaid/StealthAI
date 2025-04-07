"""
Discreet AI Coding Assistant - Main Application

This application provides invisible AI coding assistance during screen sharing sessions.
Cross-platform with enhanced macOS and Windows functionality. Optimized for macOS.
"""
import sys
import os
import logging
import platform

# Import GUI libraries with fallback
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    HAS_GUI = True
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication
        from PySide2.QtCore import QTimer
        HAS_GUI = True
    except ImportError:
        print("WARNING: GUI libraries not available. Running in CLI mode.")
        HAS_GUI = False

# Import application components
from transparent_window import TransparentWindow, HAS_PYQT
from keyboard_listener import KeyboardListener, HAS_KEYBOARD
from ai_assistant import AIAssistant
from screen_utils import ScreenSharingDetector
from config import Config

# Setup logging
logging.basicConfig(
    filename='assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Detect platform
        system = platform.system()
        is_macos = system == "Darwin"
        is_windows = system == "Windows"
        is_linux = system == "Linux"
        
        # Print welcome message with platform info
        print(f"Discreet AI Coding Assistant")
        print(f"Detected platform: {system}")
        print(f"Optimized for: {'macOS' if is_macos else 'Windows' if is_windows else 'Linux'}")
        print("=" * 50)
        
        # Initialize configuration
        config = Config()
        
        # Initialize AI Assistant
        ai_assistant = AIAssistant()
        
        # Initialize screen sharing detector
        screen_detector = ScreenSharingDetector()
        
        # macOS-specific setup
        if is_macos:
            # Check for macOS-specific dependencies
            try:
                import objc
                HAS_OBJC = True
                print("✓ PyObjC available: Enhanced macOS invisibility enabled")
            except ImportError:
                HAS_OBJC = False
                print("⚠️  PyObjC not available: Limited macOS invisibility (install with 'pip install pyobjc')")
        
        # Check if we're in GUI mode or CLI mode
        if HAS_GUI and HAS_PYQT:
            # GUI mode - Use PyQt/PySide interface
            logger.info("Starting in GUI mode")
            
            # Start Qt application
            app = QApplication(sys.argv)
            
            # Create main transparent window
            window = TransparentWindow(ai_assistant, screen_detector)
            
            # Initialize keyboard listener
            activation_shortcut = config.get("activation_shortcut", "ctrl+alt+c")
            keyboard_listener = KeyboardListener(activation_shortcut, window.toggle_visibility)
            keyboard_listener.start()
            
            # Display shortcut info
            shortcut_available = HAS_KEYBOARD
            logger.info(f"Keyboard shortcuts {'enabled' if shortcut_available else 'disabled'}")
            print(f"Activation shortcut: {activation_shortcut} {'(active)' if shortcut_available else '(DISABLED - pynput not available)'}")
            
            # Setup periodic screen sharing check
            def check_screen_sharing():
                is_sharing = screen_detector.is_screen_sharing()
                window.on_screen_sharing_change(is_sharing)
                
            timer = QTimer()
            timer.timeout.connect(check_screen_sharing)
            timer.start(2000)  # Check every 2 seconds
            
            logger.info("GUI application started successfully")
            
            # Execute application
            exit_code = app.exec_()
            
            # Clean up
            keyboard_listener.stop()
            
            return exit_code
            
        else:
            # CLI mode - Run without GUI for development/testing
            logger.info("Starting in CLI mode (GUI libraries not available)")
            print("Welcome to Coding Assistant (CLI Mode)")
            print("GUI libraries not available. Running in CLI mode for development/testing.")
            
            # Run API test to verify functionality
            test_prompt = "Write a simple function to check if a string is a palindrome."
            print(f"\nTesting AI Assistant with prompt: '{test_prompt}'")
            
            # First check if we have API key
            if not os.environ.get('OPENAI_API_KEY'):
                print("⚠️ OPENAI_API_KEY not found in environment variables.")
                print("To use the AI Assistant, please set your OpenAI API key.")
                print("Example: export OPENAI_API_KEY=your_api_key_here")
            else:
                try:
                    print("Sending request to OpenAI API...")
                    response = ai_assistant.get_coding_assistance(test_prompt, language="Python")
                    print("\nResponse from AI Assistant:")
                    print("-" * 40)
                    print(response)
                    print("-" * 40)
                except Exception as e:
                    print(f"Error testing AI Assistant: {str(e)}")
                    print("Please check your OpenAI API key and internet connection.")
            
            print("\nCLI test completed. In a normal environment with GUI libraries,")
            print("the application would launch with a transparent, draggable window.")
            
            return 0
        
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
