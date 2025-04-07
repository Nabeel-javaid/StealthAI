#!/usr/bin/env python3
"""
Test script for keyboard shortcuts functionality
This script helps verify that keyboard shortcuts are working correctly
"""
import sys
import time
import logging
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import pynput
try:
    from pynput import keyboard
    print("✅ Successfully imported pynput keyboard module")
    HAS_KEYBOARD = True
except ImportError as e:
    print(f"❌ Error importing pynput: {e}")
    HAS_KEYBOARD = False
    sys.exit(1)

def main():
    """Test keyboard listener functionality"""
    # Check platform
    system = platform.system()
    print(f"Detected platform: {system}")
    is_macos = system == "Darwin"
    
    if is_macos:
        print("Running on macOS - Command (⌘) key will be mapped to 'ctrl' in pynput")
        print("Option (⌥) key will be mapped to 'alt' in pynput")
    
    print("\nPress any key to see its representation (Ctrl+C to exit):")
    print("=" * 50)
    
    # Keep track of currently pressed keys
    current_keys = set()
    
    def on_press(key):
        """Handle key press events"""
        try:
            # Add to currently pressed keys
            current_keys.add(key)
            
            # Display key information
            key_str = str(key)
            if hasattr(key, 'char') and key.char:
                print(f"Key pressed: {key} (character: '{key.char}')")
            else:
                print(f"Special key pressed: {key}")
                
            # Show currently pressed key combination
            if len(current_keys) > 1:
                print(f"Current key combination: {current_keys}")
                
            # Check for common shortcuts on macOS
            if is_macos:
                # Command+Option+C (appears as ctrl+alt+c on macOS with pynput)
                if key == keyboard.Key.ctrl or key == keyboard.Key.alt:
                    if keyboard.Key.ctrl in current_keys and keyboard.Key.alt in current_keys:
                        for k in current_keys:
                            if hasattr(k, 'char') and k.char == 'c':
                                print("🎯 Detected Command+Option+C shortcut!")
            
        except Exception as e:
            print(f"Error in on_press: {e}")
    
    def on_release(key):
        """Handle key release events"""
        try:
            # Remove from currently pressed keys
            if key in current_keys:
                current_keys.remove(key)
                
            print(f"Key released: {key}")
            
            # Exit on Esc key
            if key == keyboard.Key.esc:
                print("Esc pressed, exiting...")
                return False
        except Exception as e:
            print(f"Error in on_release: {e}")
    
    # Set up keyboard listener
    try:
        print("Starting keyboard listener...")
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            print("Keyboard listener active. Press keys to test (Esc to exit)")
            listener.join()
    except Exception as e:
        print(f"Error with keyboard listener: {e}")
        
    print("Keyboard test completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")