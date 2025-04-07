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
    print("Successfully imported pynput keyboard module")
except ImportError as e:
    print(f"WARNING: pynput library not available ({str(e)}). Keyboard shortcuts disabled.")
    HAS_KEYBOARD = False
    # Create dummy classes for type checking
    class DummyKeyboardModule:
        class Key:
            ctrl = None
            alt = None
            shift = None
            cmd = None
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
    print("Using dummy keyboard module for testing - keyboard shortcuts will not function")
    
# Show system-specific information
system = platform.system()
if system == "Darwin":
    print("macOS detected - Command (⌘) key will be treated as ctrl in pynput")
    print("Note: On macOS, you may need to grant accessibility permissions")
    print("  System Preferences > Security & Privacy > Privacy > Accessibility")
elif system == "Linux":
    print("Linux detected - pynput may require X11 or Wayland dependencies")
    print("  For X11: sudo apt-get install python3-xlib")
    print("  For Wayland: Support may be limited")
elif system == "Windows":
    print("Windows detected - no additional dependencies needed for pynput")

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
        
        # macOS specific handling
        is_macos = platform.system() == "Darwin"
        
        # Debug logging for understanding the keyboard configuration
        if is_macos:
            logger.info("Parsing macOS shortcut: %s", shortcut_str)
            print(f"Parsing macOS shortcut: {shortcut_str}")
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(keyboard.Key.ctrl)
            elif part == 'alt':
                keys.add(keyboard.Key.alt)
            elif part == 'shift':
                keys.add(keyboard.Key.shift)
            # Handle macOS Command key (maps to cmd_* keys in pynput on macOS)
            elif part == 'cmd':
                if is_macos:
                    # On macOS, pynput implements Command key differently across versions
                    # Try different attributes that might represent Command key
                    if hasattr(keyboard.Key, 'cmd'):
                        keys.add(keyboard.Key.cmd)
                        print("Using Command (⌘) key as modifier (cmd)")
                    elif hasattr(keyboard.Key, 'cmd_l'):
                        keys.add(keyboard.Key.cmd_l)  # Left Command key
                        print("Using left Command (⌘) key as modifier (cmd_l)")
                    elif hasattr(keyboard.Key, 'command'):
                        keys.add(keyboard.Key.command)
                        print("Using Command (⌘) key as modifier (command)")
                    else:
                        # Fallback to ctrl if no cmd key available
                        keys.add(keyboard.Key.ctrl)
                        print("Using Control key as fallback for Command (⌘)")
                else:
                    # Non-macOS platform
                    if hasattr(keyboard.Key, 'cmd'):
                        keys.add(keyboard.Key.cmd)
                    else:
                        # Fallback if cmd not available
                        keys.add(keyboard.Key.ctrl)
            # macOS Option key (also known as Alt)
            elif part in ('option', 'opt'):
                if is_macos:
                    if hasattr(keyboard.Key, 'alt_l'):
                        keys.add(keyboard.Key.alt_l)  # Left Option key
                        print("Using left Option (⌥) key as modifier (alt_l)")
                    elif hasattr(keyboard.Key, 'option'):
                        keys.add(keyboard.Key.option)
                        print("Using Option (⌥) key as modifier (option)")
                    else:
                        keys.add(keyboard.Key.alt)
                        print("Using Alt key as Option (⌥) key")
                else:
                    keys.add(keyboard.Key.alt)
            elif len(part) == 1:  # Single character key
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                # Handle function keys (F1-F12)
                if part.startswith('f') and part[1:].isdigit():
                    fn_num = int(part[1:])
                    if 1 <= fn_num <= 12:
                        key_name = f"f{fn_num}"
                        keys.add(getattr(keyboard.Key, key_name))
        
        # Debug info
        print(f"Parsed shortcut '{shortcut_str}' into keys: {keys}")
                        
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
                # Debug info, especially useful on macOS
                if platform.system() == "Darwin":
                    logger.debug(f"Key pressed: {key}")
                
                # Special handling for Command key on macOS
                if platform.system() == "Darwin" and any('cmd' in str(k) for k in self.shortcut):
                    # Check if this is any variant of Command key
                    cmd_pressed = False
                    if hasattr(keyboard.Key, 'cmd') and key == keyboard.Key.cmd:
                        cmd_pressed = True
                    elif hasattr(keyboard.Key, 'cmd_l') and key == keyboard.Key.cmd_l:
                        cmd_pressed = True
                    elif hasattr(keyboard.Key, 'cmd_r') and key == keyboard.Key.cmd_r:
                        cmd_pressed = True
                    elif hasattr(keyboard.Key, 'command') and key == keyboard.Key.command:
                        cmd_pressed = True
                    
                    # If Command key is pressed, add all Command key variants to current_keys
                    # This handles when shortcut expects one variant but another is pressed
                    if cmd_pressed:
                        for k in self.shortcut:
                            if 'cmd' in str(k) or 'command' in str(k):
                                self.current_keys.add(k)
                                logger.debug(f"Added Command key variant: {k}")
                        return
                
                # Normal key handling
                if key in self.shortcut:
                    self.current_keys.add(key)
                    logger.debug(f"Added key to current keys: {key}")
                
                # Check if all shortcut keys are pressed
                if all(k in self.current_keys for k in self.shortcut):
                    logger.info(f"Shortcut triggered: {self.shortcut}")
                    self.callback()
            except Exception as e:
                logger.error(f"Error in keyboard listener on_press: {str(e)}")
                
        def on_release(key):
            try:
                # Debug info for macOS
                if platform.system() == "Darwin":
                    logger.debug(f"Key released: {key}")
                
                # Special handling for Command key on macOS
                if platform.system() == "Darwin":
                    # Check if this is any variant of Command key
                    cmd_released = False
                    if hasattr(keyboard.Key, 'cmd') and key == keyboard.Key.cmd:
                        cmd_released = True
                    elif hasattr(keyboard.Key, 'cmd_l') and key == keyboard.Key.cmd_l:
                        cmd_released = True
                    elif hasattr(keyboard.Key, 'cmd_r') and key == keyboard.Key.cmd_r:
                        cmd_released = True
                    elif hasattr(keyboard.Key, 'command') and key == keyboard.Key.command:
                        cmd_released = True
                    
                    # If Command key is released, remove all Command key variants from current_keys
                    if cmd_released:
                        cmd_keys_to_remove = []
                        for k in self.current_keys:
                            if 'cmd' in str(k) or 'command' in str(k):
                                cmd_keys_to_remove.append(k)
                        
                        for k in cmd_keys_to_remove:
                            self.current_keys.remove(k)
                            logger.debug(f"Removed Command key variant: {k}")
                        return
                
                # Normal key handling
                if key in self.current_keys:
                    self.current_keys.remove(key)
                    logger.debug(f"Removed key from current keys: {key}")
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
