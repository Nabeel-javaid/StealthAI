#!/usr/bin/env python3
"""
Debug version of the app that shows the GUI immediately
This helps when troubleshooting keyboard shortcut issues
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
    """Debug mode entry point (shows window immediately)"""
    try:
        # Detect platform
        system = platform.system()
        is_macos = system == "Darwin"
        
        # Print welcome message with platform info
        print(f"Discreet AI Coding Assistant for macOS (DEBUG MODE)")
        print(f"Detected platform: {system}")
        
        # Check if running on macOS
        if not is_macos:
            print("⚠️  Warning: This application is designed for macOS only.")
            print("Some features may not work correctly on this platform.")
        
        print("=" * 50)
        print("DEBUG MODE: Window will be shown automatically")
        print("=" * 50)
        
        # Initialize configuration
        config = Config()
        
        # Initialize AI Assistant
        ai_assistant = AIAssistant()
        
        # Initialize screen sharing detector
        screen_detector = ScreenSharingDetector()
        
        # GUI mode with PyQt/PySide available
        if HAS_GUI and HAS_PYQT:
            app = QApplication(sys.argv)
            
            # Create main transparent window
            window = TransparentWindow(ai_assistant, screen_detector)
            
            # Initialize keyboard listener with macOS-specific shortcut 
            # (cmd+option+c is more natural on macOS than ctrl+alt+c)
            activation_shortcut = config.get("activation_shortcut", "cmd+alt+c")
            keyboard_listener = KeyboardListener(activation_shortcut, window.toggle_visibility)
            keyboard_listener.start()
            
            # Display shortcut info
            shortcut_available = HAS_KEYBOARD
            logger.info(f"Keyboard shortcuts {'enabled' if shortcut_available else 'disabled'}")
            print(f"Activation shortcut: {activation_shortcut} {'(active)' if shortcut_available else '(DISABLED - pynput not available)'}")
            
            # macOS-specific shortcut info
            if is_macos:
                print("   Note: On macOS, 'cmd' is the Command ⌘ key and 'alt' is the Option ⌥ key")
            
            # Setup periodic screen sharing check
            def check_screen_sharing():
                is_sharing = screen_detector.is_screen_sharing()
                window.on_screen_sharing_change(is_sharing)
                
            timer = QTimer()
            timer.timeout.connect(check_screen_sharing)
            timer.start(2000)  # Check every 2 seconds
            
            # DEBUG MODE: Show window immediately
            print("Making window visible immediately...")
            window.show()
            window.is_visible = True
            
            logger.info("GUI application started successfully in debug mode")
            
            # Execute application
            exit_code = app.exec_()
            
            # Clean up
            keyboard_listener.stop()
            
            return exit_code
            
        else:
            # CLI mode - Run without GUI for development/testing
            print("Cannot start in debug mode - GUI libraries not available.")
            return 1
        
    except Exception as e:
        logger.error(f"Error in debug mode: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())