"""
Keyboard listener for detecting hotkeys/shortcuts
Cross-platform implementation with fallback for environments where pynput isn't available
"""
import logging
import threading
import platform

# Try to import keyboard library with fallback for environments without pynput
try:
    from pynput import keyboard as pynput_keyboard
    HAS_KEYBOARD = True
    keyboard = pynput_keyboard
except ImportError:
    print("WARNING: pynput library not available. Keyboard shortcuts disabled.")
    HAS_KEYBOARD = False
    # Create dummy classes for type checking
    class DummyKeyboardModule:
        class Key:
            ctrl = None
            alt = None
            shift = None
            f1 = f2 = f3 = f4 = f5 = f6 = f7 = f8 = f9 = f10 = f11 = f12 = None
        class KeyCode:
            @staticmethod
            def from_char(c): 
                return c
        class Listener:
            def __init__(self, on_press=None, on_release=None): pass
            def start(self): pass
            def join(self): pass
            def stop(self): pass
    
    # Use the dummy module
    keyboard = DummyKeyboardModule()

logger = logging.getLogger(__name__)

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
        self.shortcut = self._parse_shortcut(shortcut)
        self.callback = callback
        self.current_keys = set()
        self.listener = None
        self.active = False
        self.thread = None
        
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
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl)
            elif part == 'alt':
                keys.add(keyboard.Key.alt)
            elif part == 'shift':
                keys.add(keyboard.Key.shift)
            elif len(part) == 1:  # Single character key
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                # Handle function keys (F1-F12)
                if part.startswith('f') and part[1:].isdigit():
                    fn_num = int(part[1:])
                    if 1 <= fn_num <= 12:
                        key_name = f"f{fn_num}"
                        keys.add(getattr(keyboard.Key, key_name))
                        
        return keys
        
    def start(self):
        """Start listening for keyboard shortcuts"""
        if self.active:
            return
            
        self.active = True
        
        # Skip if keyboard library not available
        if not HAS_KEYBOARD:
            logger.warning("Keyboard shortcuts disabled: pynput library not available")
            print(f"Keyboard shortcuts disabled. Would have used: {str(self.shortcut)}")
            return
        
        def on_press(key):
            try:
                if key in self.shortcut:
                    self.current_keys.add(key)
                    
                # Check if all shortcut keys are pressed
                if all(k in self.current_keys for k in self.shortcut):
                    self.callback()
            except Exception as e:
                logger.error(f"Error in keyboard listener on_press: {str(e)}")
                
        def on_release(key):
            try:
                if key in self.current_keys:
                    self.current_keys.remove(key)
            except Exception as e:
                logger.error(f"Error in keyboard listener on_release: {str(e)}")
                
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        
        # Start listener in a separate thread
        self.thread = threading.Thread(target=self._run_listener)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Keyboard listener started with shortcut: {self.shortcut}")
        
    def _run_listener(self):
        """Run the keyboard listener"""
        if not HAS_KEYBOARD or not self.listener:
            logger.warning("Cannot run keyboard listener - library or listener not available")
            return
            
        try:
            self.listener.start()
            self.listener.join()
        except Exception as e:
            logger.error(f"Error in keyboard listener thread: {str(e)}")
            self.active = False
            
    def stop(self):
        """Stop listening for keyboard shortcuts"""
        if self.active:
            self.active = False
            
            # Only try to stop listener if it exists and keyboard library is available
            if HAS_KEYBOARD and self.listener:
                try:
                    self.listener.stop()
                except Exception as e:
                    logger.error(f"Error stopping keyboard listener: {str(e)}")
                
            logger.info("Keyboard listener stopped")
