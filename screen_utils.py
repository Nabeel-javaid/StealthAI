"""
Screen utilities for detecting screen sharing (Cross-platform implementation)
"""
import os
import subprocess
import logging
import sys
import platform

# Try to import psutil, but don't fail if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    print("WARNING: psutil library not available. Screen sharing detection will be limited.")
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

class ScreenSharingDetector:
    """
    Utility class to detect if screen sharing is active
    This version is designed to work cross-platform, with enhanced functionality on Windows
    """
    
    def __init__(self):
        """Initialize the screen sharing detector"""
        self.screen_sharing_apps = [
            # Windows
            "Zoom.exe", "Teams.exe", "msTeams.exe", "slack.exe", 
            "DiscordPTB.exe", "Discord.exe", "WebexHost.exe", "Webex.exe",
            "GoogleMeet.exe", "chrome.exe", "msedge.exe", "firefox.exe", 
            "safari.exe", "brave.exe", "opera.exe",
            # macOS/Linux
            "zoom", "teams", "slack", "discord", "webex", "chrome", 
            "firefox", "safari", "brave", "opera"
        ]
        self.last_result = False
        self.cache_time = 0
        self.is_windows = platform.system() == "Windows"
        
        # In development mode (not on Windows), we'll use a simulated status
        self.dev_mode = not self.is_windows
        self.simulated_sharing = False
        
    def is_screen_sharing(self):
        """
        Check if screen sharing is likely active
        
        Returns:
            bool: True if screen sharing is detected, False otherwise
        """
        # In development mode, return the simulated status
        if self.dev_mode:
            return self.simulated_sharing
            
        try:
            # Method 1: Check if known screen sharing processes are running (needs psutil)
            if HAS_PSUTIL:
                for process in psutil.process_iter(['pid', 'name']):
                    if any(app.lower() in process.info['name'].lower() for app in self.screen_sharing_apps):
                        # Found a potential screen sharing app, check if it's in screen sharing mode
                        if self._check_sharing_mode(process.info['pid']):
                            return True
                        
            # Method 2: On Windows, check window titles (skipped in dev mode)
            if self.is_windows:
                try:
                    # Import Windows-specific modules only on Windows
                    import win32gui
                    
                    sharing_indicators = [
                        "Screen Sharing", "sharing your screen", "presenting", 
                        "is being shared", "screen share", "remote control"
                    ]
                    
                    def check_window(hwnd, _):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if any(indicator.lower() in title.lower() for indicator in sharing_indicators):
                                nonlocal found_sharing
                                found_sharing = True
                        return True
                        
                    found_sharing = False
                    win32gui.EnumWindows(check_window, None)
                    
                    return found_sharing
                except ImportError:
                    logger.warning("win32gui module not available")
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting screen sharing: {str(e)}")
            return False
            
    def _check_sharing_mode(self, pid):
        """
        Check if process with given PID is likely in screen sharing mode
        
        Args:
            pid (int): Process ID to check
            
        Returns:
            bool: True if likely sharing, False otherwise
        """
        if not HAS_PSUTIL:
            return False
            
        try:
            process = psutil.Process(pid)
            # Check CPU and memory usage as indicators
            # Screen sharing typically increases CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_percent = process.memory_percent()
            
            # If high resource usage, might be sharing
            if cpu_percent > 15 and memory_percent > 2.0:
                return True
                
            return False
        except:
            return False
    
    def get_foreground_window_info(self):
        """
        Get information about the foreground window
        
        Returns:
            dict: Information about foreground window
        """
        if self.dev_mode:
            return {
                "pid": 0,
                "name": "development_mode",
                "title": "Development Mode (Simulated Window)",
                "executable": "python"
            }
        
        # Windows-specific implementation using win32gui
        if self.is_windows:
            try:
                # Import Windows-specific modules only on Windows
                import win32gui
                import win32process
                
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # Only use psutil if available
                if HAS_PSUTIL:
                    process = psutil.Process(pid)
                    name = process.name()
                    executable = process.exe() 
                else:
                    name = "Unknown"
                    executable = "Unknown"
                
                return {
                    "pid": pid,
                    "name": name,
                    "title": win32gui.GetWindowText(hwnd),
                    "executable": executable
                }
            except Exception as e:
                logger.error(f"Error getting foreground window info: {str(e)}")
        
        # Fallback for non-Windows or if Windows-specific code fails
        if HAS_PSUTIL:
            try:
                # Get active process info using psutil
                current_pid = os.getpid()
                process = psutil.Process(current_pid)
                
                return {
                    "pid": current_pid,
                    "name": process.name(),
                    "title": "Active Window",
                    "executable": process.exe() if hasattr(process, "exe") else sys.executable
                }
            except Exception as e:
                logger.error(f"Error getting process info: {str(e)}")
        
        # Ultimate fallback when nothing else works
        return {
            "pid": 0,
            "name": "python",
            "title": "Python Application",
            "executable": sys.executable
        }
