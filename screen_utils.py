"""
Screen utilities for detecting screen sharing on macOS
Advanced detection methods for popular screen sharing applications like Zoom, Teams, and Meet
on Apple platforms with enhanced invisibility features
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
    Utility class to detect if screen sharing is active on macOS
    This version is optimized for macOS with advanced detection for Zoom, Teams,
    and other popular screen sharing applications used on Apple platforms
    """
    
    def __init__(self):
        """Initialize the screen sharing detector"""
        # Define OS-specific platform
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # OS-specific screen sharing applications
        if self.is_windows:
            self.screen_sharing_apps = [
                "Zoom.exe", "Teams.exe", "msTeams.exe", "slack.exe", 
                "DiscordPTB.exe", "Discord.exe", "WebexHost.exe", "Webex.exe",
                "GoogleMeet.exe", "chrome.exe", "msedge.exe", "firefox.exe", 
                "safari.exe", "brave.exe", "opera.exe"
            ]
        elif self.is_macos:
            # Comprehensive list of macOS applications that can share screens
            self.screen_sharing_apps = [
                # Video conferencing apps
                "zoom.us", "Microsoft Teams", "Slack", "Discord",
                "Webex", "Webex Meeting", "WebexHelper", 
                "Google Meet", "join.me", "BlueJeans", "GoToMeeting",
                "RingCentral", "Skype", "Skype for Business", 
                # Browsers
                "Google Chrome", "Firefox", "Safari", "Brave Browser", 
                "Opera", "Microsoft Edge", "Arc",
                # Screen recording/streaming apps
                "QuickTime Player", "OBS Studio", "ScreenFlow", "Camtasia",
                "Loom", "Screen Studio", "CleanShot X", "TeamViewer",
                # Apple native screen sharing
                "Screen Sharing", "AppleVNCServer", "Photo Booth",
                # Remote access tools
                "AnyDesk", "VNC Viewer", "VNC Server", "Jump Desktop",
                "Screens", "LogMeIn", "Chrome Remote Desktop"
            ]
        else:  # Linux and other platforms
            self.screen_sharing_apps = [
                "zoom", "teams", "slack", "discord", "webex", "chrome", 
                "firefox", "safari", "brave", "opera"
            ]

        self.last_result = False
        self.cache_time = 0
        
        # In development mode, we'll use a simulated status
        self.dev_mode = not (self.is_windows or self.is_macos)
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
                        
            # Method 2: Platform-specific window title checks
            # Windows implementation
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
                    
            # macOS implementation - check for screen sharing indicators
            elif self.is_macos:
                try:
                    # First try: Use native macOS APIs through PyObjC if available
                    # This is the most reliable method but requires PyObjC
                    try:
                        # Try using native macOS APIs with PyObjC
                        import objc
                        from Foundation import NSBundle
                        
                        # Load the CoreGraphics framework to get access to CGWindowListCopyWindowInfo
                        cg = NSBundle.bundleWithIdentifier_('com.apple.CoreGraphics')
                        functions = [
                            ('CGWindowListCopyWindowInfo', b'@@I^{__CFString=}'),
                            ('kCGWindowListOptionOnScreenOnly', b'I'),
                            ('kCGNullWindowID', b'I'),
                            ('kCGWindowOwnerName', b'@'),
                            ('kCGWindowName', b'@')
                        ]
                        
                        # Register the functions and constants with the runtime
                        objc.loadBundleFunctions(cg, globals(), functions)
                        
                        # Get the list of windows
                        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
                        
                        # Look for window titles and owner names related to screen sharing
                        sharing_indicators = [
                            "screen sharing", "sharing screen", "presenting", "screen share", 
                            "is shared", "remote control", "stop sharing", "stop share",
                            "you are presenting", "viewing your screen", "zoom.us share", "teams sharing"
                        ]
                        
                        for window in window_list:
                            # Check window owner (app name)
                            if kCGWindowOwnerName in window:
                                app_name = window[kCGWindowOwnerName]
                                if any(app.lower() in str(app_name).lower() for app in self.screen_sharing_apps):
                                    logger.debug(f"Found potential screen sharing app: {app_name}")
                                    
                                    # If it's known to be a screen sharing app, check if it has sharing indicators
                                    if kCGWindowName in window and window[kCGWindowName]:
                                        window_title = window[kCGWindowName]
                                        if any(indicator in str(window_title).lower() for indicator in sharing_indicators):
                                            logger.info(f"Detected screen sharing: {app_name} - {window_title}")
                                            return True
                        
                        # Check for AXWindowSharesVideoContent using accessibility API
                        try:
                            # Load the Accessibility framework
                            from Cocoa import NSWorkspace, NSRunningApplication
                            
                            # Get frontmost application
                            workspace = NSWorkspace.sharedWorkspace()
                            frontmost_app = workspace.frontmostApplication()
                            
                            # Check if this is a potential screen sharing app
                            if frontmost_app and frontmost_app.localizedName():
                                app_name = frontmost_app.localizedName()
                                if any(app.lower() in str(app_name).lower() for app in self.screen_sharing_apps):
                                    logger.debug(f"Checking AXWindowSharesVideoContent for: {app_name}")
                                    # This app might be sharing the screen
                                    # We would check AXWindowSharesVideoContent here if we had proper permissions
                                    # Since this requires special permissions, we'll use process-based detection instead
                                    return True
                        except Exception as e:
                            logger.debug(f"Unable to use AXWindowSharesVideoContent: {e}")
                        
                    except ImportError as e:
                        logger.debug(f"PyObjC not available, falling back to command-line checks: {e}")
                        # Continue with fallback methods
                    
                    # Fallback method 1: Look for specific macOS processes related to screen sharing
                    mac_sharing_processes = [
                        "ScreenSharing", "screencapture", "QuickTime Player", 
                        "ScreenCaptureKit", "com.apple.screensharing", "avconferenced",
                        "ShareKit", "ScreensharingAgent", "screencaptureui", "corescreend"
                    ]
                    
                    # Fallback method 2: Check for screen sharing system service status
                    # This runs an AppleScript that checks for processes related to screen sharing
                    service_check_cmd = """
                    osascript -e 'do shell script "ps aux | grep -v grep | grep -E \\"Screen Sharing|ScreenSharing|screencapture|screencaptureui\\"" 2>/dev/null || exit 0'
                    """
                    
                    try:
                        result = subprocess.run(service_check_cmd, shell=True, text=True, capture_output=True)
                        if result.returncode == 0 and result.stdout.strip():
                            logger.info("Detected screen sharing through system services")
                            return True
                    except Exception as e:
                        logger.debug(f"Error checking screen sharing services: {e}")
                    
                    # Fallback method 3: Try to detect Zoom screen sharing
                    # This is more reliable and doesn't require accessibility permissions
                    has_zoom = False
                    
                    try:
                        result = subprocess.run("ps aux | grep -v grep | grep -i 'zoom.us'", 
                                             shell=True, text=True, capture_output=True)
                        has_zoom = result.returncode == 0 and "zoom.us" in result.stdout
                        
                        if has_zoom:
                            # Check if Zoom is in screen sharing mode by looking for specific Zoom processes
                            sharing_check = subprocess.run(
                                "ps aux | grep -v grep | grep -i 'zoom.us' | grep -i 'sharing'", 
                                shell=True, text=True, capture_output=True)
                            
                            if sharing_check.returncode == 0 and sharing_check.stdout.strip():
                                logger.info("Detected Zoom screen sharing")
                                return True
                    except Exception as e:
                        logger.debug(f"Error checking Zoom screen sharing: {e}")
                    
                    # Fallback method 4: Check for Microsoft Teams screen sharing
                    has_teams = False
                    
                    try:
                        result = subprocess.run("ps aux | grep -v grep | grep -i 'Microsoft Teams'", 
                                             shell=True, text=True, capture_output=True)
                        has_teams = result.returncode == 0 and "Microsoft Teams" in result.stdout
                        
                        if has_teams:
                            # Teams creates specific processes when sharing
                            sharing_check = subprocess.run(
                                "ps aux | grep -v grep | grep -i 'Teams' | grep -E 'share|screen'", 
                                shell=True, text=True, capture_output=True)
                            
                            if sharing_check.returncode == 0 and sharing_check.stdout.strip():
                                logger.info("Detected Microsoft Teams screen sharing")
                                return True
                    except Exception as e:
                        logger.debug(f"Error checking Teams screen sharing: {e}")
                    
                    # As a final fallback, we check if any screen recording/sharing processes are running
                    for process in mac_sharing_processes:
                        try:
                            cmd = f"ps aux | grep -v grep | grep -i '{process}'"
                            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                            if result.returncode == 0 and result.stdout.strip():
                                logger.info(f"Detected screen sharing process: {process}")
                                return True
                        except Exception as e:
                            logger.debug(f"Error checking process {process}: {e}")
                    
                    tcc_check_cmd = """
                    osascript -e 'do shell script "lsof 2>/dev/null | grep TCC.db | grep -v grep"'
                    """
                    
                    # 7. Check for CoreMedia frameworks in use by video conferencing apps
                    coremedia_check_cmd = """
                    osascript -e 'do shell script "lsof 2>/dev/null | grep CoreMedia | grep -v grep"'
                    """
                    
                    # Check process list for known screen sharing processes
                    if HAS_PSUTIL:
                        for proc in psutil.process_iter(['name']):
                            proc_name = proc.info['name'] if 'name' in proc.info else ""
                            if any(sharing_app.lower() in proc_name.lower() for sharing_app in mac_sharing_processes):
                                logger.info(f"Screen sharing detected: Found process {proc_name}")
                                return True
                    
                    # Execute all the check commands
                    try:
                        # Check for screen sharing service status
                        service_result = subprocess.run(
                            service_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if service_result.stdout.strip():
                            logger.info("Screen sharing detected: Screen sharing service is active")
                            return True
                    except Exception as e:
                        logger.debug(f"Failed to check screen sharing service: {e}")
                    
                    try:
                        # Check for Zoom screen sharing
                        zoom_result = subprocess.run(
                            zoom_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if zoom_result.stdout.strip() and "error" not in zoom_result.stdout.lower():
                            logger.info("Screen sharing detected: Zoom is sharing screen")
                            return True
                    except Exception:
                        # Ignore errors when Zoom isn't running
                        pass
                    
                    try:
                        # Check for Teams screen sharing
                        teams_result = subprocess.run(
                            teams_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if teams_result.stdout.strip().lower() == 'true':
                            logger.info("Screen sharing detected: Microsoft Teams is sharing screen")
                            return True
                    except Exception:
                        # Ignore errors when Teams isn't running
                        pass
                    
                    try:
                        # Check for screen sharing daemon
                        daemon_result = subprocess.run(
                            daemon_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if daemon_result.stdout.strip():
                            logger.info("Screen sharing detected: screensharingd is running")
                            return True
                    except Exception as e:
                        logger.debug(f"Failed to check screen sharing daemon: {e}")
                    
                    try:
                        # Check for screen recording indicator
                        recording_result = subprocess.run(
                            recording_indicator_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if recording_result.stdout.strip().lower() == 'true':
                            logger.info("Screen sharing detected: Screen recording indicator visible")
                            return True
                    except Exception as e:
                        logger.debug(f"Failed to check recording indicator: {e}")
                    
                    try:
                        # Check for TCC.db access (screen capture permissions in use)
                        tcc_result = subprocess.run(
                            tcc_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if tcc_result.stdout.strip():
                            for app in self.screen_sharing_apps:
                                if app.lower() in tcc_result.stdout.lower():
                                    logger.info(f"Screen sharing detected: {app} is accessing screen capture permissions")
                                    return True
                    except Exception as e:
                        logger.debug(f"Failed to check TCC database: {e}")
                    
                    try:
                        # Check for CoreMedia usage by conferencing apps
                        coremedia_result = subprocess.run(
                            coremedia_check_cmd, 
                            shell=True, 
                            text=True, 
                            capture_output=True, 
                            timeout=1
                        )
                        if coremedia_result.stdout.strip():
                            for app in self.screen_sharing_apps:
                                if app.lower() in coremedia_result.stdout.lower():
                                    logger.info(f"Screen sharing detected: {app} is using CoreMedia frameworks")
                                    return True
                    except Exception as e:
                        logger.debug(f"Failed to check CoreMedia usage: {e}")
                    
                    return False
                except Exception as e:
                    logger.error(f"Error checking macOS screen sharing: {str(e)}")
                    return False
            
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
        
        # macOS-specific implementation
        elif self.is_macos:
            try:
                # Use AppleScript to get foreground window info
                applescript = """
                osascript -e 'tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    set frontAppWindow to ""
                    try
                        set frontAppWindow to name of front window of application process frontApp
                    end try
                    return frontApp & "," & frontAppWindow
                end tell'
                """
                
                result = subprocess.run(applescript, shell=True, text=True, capture_output=True)
                output = result.stdout.strip().split(",")
                
                app_name = output[0] if len(output) > 0 else "Unknown"
                window_title = output[1] if len(output) > 1 else ""
                
                # Get PID and executable if psutil is available
                pid = 0
                executable = ""
                
                if HAS_PSUTIL:
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        if app_name.lower() in proc.info['name'].lower():
                            pid = proc.info['pid']
                            executable = proc.info['exe'] if 'exe' in proc.info else ""
                            break
                
                return {
                    "pid": pid,
                    "name": app_name,
                    "title": window_title or app_name,
                    "executable": executable
                }
            except Exception as e:
                logger.error(f"Error getting macOS foreground window info: {str(e)}")
        
        # Fallback for other platforms or if platform-specific code fails
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
