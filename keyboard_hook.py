#!/usr/bin/env python3
"""
Keyboard hook for macOS to show/hide the StealthAI overlay

This script sets up a keyboard listener to detect the
keyboard shortcut for showing/hiding the StealthAI overlay.
"""
import threading
import logging
import time
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import keyboard module
try:
    from pynput import keyboard
    
    # Print success message
    print("Successfully imported pynput keyboard module")
    
    # Detect platform
    system = platform.system()
    if system == "Darwin":
        print("macOS detected - Command (⌘) key will be treated as ctrl in pynput")
        print("Note: On macOS, you may need to grant accessibility permissions")
        print("  System Preferences > Security & Privacy > Privacy > Accessibility")
    elif system == "Linux":
        print("Linux detected - pynput may require X11 or Wayland dependencies")
        print("  For X11: sudo apt-get install python3-xlib")
        print("  For Wayland: Support may be limited")
    HAS_KEYBOARD = True
except ImportError:
    # Print warning
    print("WARNING: pynput library not available (No module named 'pynput'). Keyboard shortcuts disabled.")
    print("Using dummy keyboard module for testing - keyboard shortcuts will not function")
    
    # Create dummy keyboard module
    class DummyKeyboardModule:
        class Key:
            ctrl = None
            alt = None
            shift = None
            cmd = None
            f1 = f2 = f3 = f4 = f5 = f6 = f7 = f8 = f9 = f10 = f11 = f12 = None
        class KeyCode:
            @staticmethod
            def from_char(c): return c
            
        class Listener:
            def __init__(self, on_press=None, on_release=None): pass
            def start(self): pass
            def join(self): pass
            def stop(self): pass
            
    keyboard = DummyKeyboardModule()
    HAS_KEYBOARD = False


class KeyboardListener:
    """
    Listens for keyboard shortcuts and triggers actions
    """
    
    def __init__(self, shortcut, callback):
        """
        Initialize keyboard listener
        
        Args:
            shortcut (str): Keyboard shortcut (e.g., 'ctrl+shift+a')
            callback (function): Function to call when shortcut is pressed
        """
        self.callback = callback
        self.current_keys = set()
        self.pressed_sequence = []
        self.listener = None
        self.listening = False
        self.shortcut_keys = self._parse_shortcut(shortcut)
        
        # Log parsed shortcut
        logger.info(f"Parsed shortcut '{shortcut}' into keys: {self.shortcut_keys}")
    
    def _parse_shortcut(self, shortcut_str):
        """
        Parse shortcut string into component keys
        
        Args:
            shortcut_str (str): Shortcut string (e.g., 'ctrl+shift+a')
            
        Returns:
            set: Set of key objects
        """
        keys = set()
        parts = shortcut_str.lower().split('+')
        
        # Fix platform-specific keys
        system = platform.system()
        is_macos = system == "Darwin"
        
        if is_macos and 'cmd' in parts:
            # Handle the Command key
            print(f"Using Command (⌘) key as modifier (cmd)")
        
        for part in parts:
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl)
            elif part == 'alt':
                keys.add(keyboard.Key.alt)
            elif part == 'shift':
                keys.add(keyboard.Key.shift)
            elif part == 'cmd' or part == 'command':
                # On macOS, cmd is the Command key (⌘)
                # In pynput, this is mapped to keyboard.Key.cmd 
                keys.add(keyboard.Key.cmd)
            elif len(part) == 1:
                # Regular character key
                keys.add(part)
            elif part.startswith('f') and part[1:].isdigit():
                # Function keys (F1-F12)
                f_num = int(part[1:])
                if 1 <= f_num <= 12:
                    f_key = getattr(keyboard.Key, f'f{f_num}')
                    keys.add(f_key)
            else:
                # Try to get key by name
                try:
                    key = getattr(keyboard.Key, part)
                    keys.add(key)
                except AttributeError:
                    logger.warning(f"Unknown key in shortcut: {part}")
        
        return keys
    
    def start(self):
        """Start listening for keyboard shortcuts"""
        if not HAS_KEYBOARD:
            logger.warning("Keyboard shortcuts disabled - pynput library not available")
            return
        
        self.listening = True
        
        def on_press(key):
            try:
                # Convert alphanumeric key to string
                if hasattr(key, 'char') and key.char:
                    key_value = key.char.lower()
                elif hasattr(key, 'name') and isinstance(key.name, str):
                    key_value = key.name.lower()
                else:
                    key_value = key
                
                # Add to current keys
                self.current_keys.add(key_value)
                
                # Check if shortcut is pressed
                if self._check_shortcut():
                    logger.info("Shortcut detected, triggering callback")
                    self.callback()
            except Exception as e:
                logger.error(f"Error in keyboard press handler: {str(e)}")
        
        def on_release(key):
            try:
                # Convert alphanumeric key to string
                if hasattr(key, 'char') and key.char:
                    key_value = key.char.lower()
                elif hasattr(key, 'name') and isinstance(key.name, str):
                    key_value = key.name.lower()
                else:
                    key_value = key
                
                # Remove from current keys
                self.current_keys.discard(key_value)
            except Exception as e:
                logger.error(f"Error in keyboard release handler: {str(e)}")
        
        # Start listener in a separate thread
        self.thread = threading.Thread(target=self._run_listener)
        self.thread.daemon = True
        self.thread.start()
    
    def _run_listener(self):
        """Run the keyboard listener"""
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            self.listener = listener
            listener.join()
    
    def _on_press(self, key):
        """Handle key press event"""
        try:
            # Add to current keys
            self.current_keys.add(key)
            
            # Check if shortcut is pressed
            if self._check_shortcut():
                logger.info("Shortcut detected, triggering callback")
                self.callback()
        except Exception as e:
            logger.error(f"Error in keyboard press handler: {str(e)}")
    
    def _on_release(self, key):
        """Handle key release event"""
        try:
            # Remove from current keys
            if key in self.current_keys:
                self.current_keys.remove(key)
        except Exception as e:
            logger.error(f"Error in keyboard release handler: {str(e)}")
    
    def _check_shortcut(self):
        """Check if the shortcut is currently pressed"""
        # Check if all required keys are pressed
        return self.shortcut_keys.issubset(self.current_keys)
    
    def stop(self):
        """Stop listening for keyboard shortcuts"""
        self.listening = False
        if self.listener:
            self.listener.stop()


if __name__ == "__main__":
    """Test keyboard listener"""
    def key_callback():
        print("\n🎯 SHORTCUT ACTIVATED!")
    
    # Define shortcut based on platform
    is_macos = platform.system() == "Darwin"
    shortcut = "cmd+alt+c" if is_macos else "ctrl+alt+c"
    
    print("\n" + "=" * 50)
    print("Keyboard Shortcut Test")
    print("=" * 50)
    print(f"Press {shortcut} to activate shortcut")
    print("Press Ctrl+C to exit")
    
    # Create and start keyboard listener
    listener = KeyboardListener(shortcut, key_callback)
    listener.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        listener.stop()