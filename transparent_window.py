"""
Transparent window implementation that is invisible during screen sharing (Cross-platform)
"""
import sys
import logging
import platform
import os
import threading

# Import PyQt5 components for UI (or alternatives if not available)
try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
        QPushButton, QLabel, QComboBox, QApplication,
        QCheckBox
    )
    from PyQt5.QtCore import Qt, QTimer, QEvent
    from PyQt5.QtGui import QColor, QPalette, QFont
    HAS_PYQT = True
except ImportError:
    try:
        # Try PySide2 as an alternative
        from PySide2.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
            QPushButton, QLabel, QComboBox, QApplication,
            QCheckBox
        )
        from PySide2.QtCore import Qt, QTimer, QEvent
        from PySide2.QtGui import QColor, QPalette, QFont
        HAS_PYQT = True
    except ImportError:
        # For development environments without GUI libraries
        print("WARNING: Neither PyQt5 nor PySide2 is available. GUI functionality disabled.")
        HAS_PYQT = False
        # Create dummy classes for type checking
        class QWidget: pass
        class QEvent: 
            @staticmethod
            def registerEventType(): return 9999
            class Type: pass
        class Qt:
            FramelessWindowHint = 0
            WindowStaysOnTopHint = 0
            Tool = 0
            WA_TranslucentBackground = 0
            LeftButton = 0

logger = logging.getLogger(__name__)

class TransparentWindow(QWidget):
    """
    A transparent window that is invisible during screen sharing
    """
    
    def __init__(self, ai_assistant, screen_detector):
        """
        Initialize the transparent window
        
        Args:
            ai_assistant (AIAssistant): AI Assistant instance
            screen_detector (ScreenSharingDetector): Screen sharing detector
        """
        super().__init__()
        
        self.ai_assistant = ai_assistant
        self.screen_detector = screen_detector
        self.is_visible = False
        self.is_screen_sharing = False
        
        self._init_ui()
        self._setup_window_flags()
        
    def _init_ui(self):
        """Initialize the user interface"""
        # Set window title and size
        self.setWindowTitle("Coding Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create header with information
        header_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: white;")
        header_layout.addWidget(self.status_label)
        
        self.sharing_indicator = QLabel("Screen Sharing: Off")
        self.sharing_indicator.setStyleSheet("color: white;")
        header_layout.addWidget(self.sharing_indicator)
        
        # Development mode controls
        if platform.system() != "Windows":
            dev_layout = QHBoxLayout()
            
            # Add simulation toggle for testing
            self.simulate_sharing_checkbox = QCheckBox("Simulate Screen Sharing")
            self.simulate_sharing_checkbox.setStyleSheet("color: white;")
            self.simulate_sharing_checkbox.toggled.connect(self._toggle_simulated_sharing)
            dev_layout.addWidget(self.simulate_sharing_checkbox)
            
            # Add a dev mode label
            dev_mode_label = QLabel("(Development Mode)")
            dev_mode_label.setStyleSheet("color: orange;")
            dev_layout.addWidget(dev_mode_label)
            
            header_layout.addLayout(dev_layout)
        
        # Language selector
        language_layout = QHBoxLayout()
        language_label = QLabel("Language:")
        language_label.setStyleSheet("color: white;")
        language_layout.addWidget(language_label)
        
        self.language_selector = QComboBox()
        self.language_selector.addItems([
            "Python", "JavaScript", "Java", "C++", "C#", "Go", 
            "Ruby", "Swift", "Kotlin", "PHP", "Rust", "TypeScript"
        ])
        language_layout.addWidget(self.language_selector)
        header_layout.addLayout(language_layout)
        
        main_layout.addLayout(header_layout)
        
        # Create input section
        input_layout = QVBoxLayout()
        
        input_label = QLabel("Problem Description:")
        input_label.setStyleSheet("color: white;")
        input_layout.addWidget(input_label)
        
        self.problem_input = QTextEdit()
        self.problem_input.setStyleSheet("""
            background-color: rgba(20, 20, 20, 0.7);
            color: white;
            border: 1px solid #444;
        """)
        self.problem_input.setPlaceholderText("Describe the coding problem or paste the question here...")
        input_layout.addWidget(self.problem_input)
        
        code_label = QLabel("Your Code (Optional):")
        code_label.setStyleSheet("color: white;")
        input_layout.addWidget(code_label)
        
        self.code_input = QTextEdit()
        self.code_input.setStyleSheet("""
            background-color: rgba(20, 20, 20, 0.7);
            color: white;
            border: 1px solid #444;
            font-family: Consolas, Monaco, monospace;
        """)
        self.code_input.setPlaceholderText("Paste your code here if you want it analyzed...")
        input_layout.addWidget(self.code_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("Get Help")
        self.submit_button.clicked.connect(self.get_ai_help)
        button_layout.addWidget(self.submit_button)
        
        self.analyze_button = QPushButton("Analyze Code")
        self.analyze_button.clicked.connect(self.analyze_code)
        button_layout.addWidget(self.analyze_button)
        
        # Add macOS specific button if on macOS
        if platform.system() == "Darwin":
            self.macos_button = QPushButton("macOS Tips")
            self.macos_button.clicked.connect(self.get_macos_advice)
            self.macos_button.setToolTip("Get macOS-specific advice for this problem")
            button_layout.addWidget(self.macos_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_inputs)
        button_layout.addWidget(self.clear_button)
        
        input_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)
        
        # Create output section
        output_label = QLabel("AI Assistant Response:")
        output_label.setStyleSheet("color: white;")
        main_layout.addWidget(output_label)
        
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setStyleSheet("""
            background-color: rgba(20, 20, 20, 0.7);
            color: white;
            border: 1px solid #444;
        """)
        main_layout.addWidget(self.response_output)
        
        # Set layout
        self.setLayout(main_layout)
        
        # Initial state is hidden
        self.hide()
        
    def _setup_window_flags(self):
        """Setup window flags to make it transparent and on top"""
        # Set window to be frameless
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # No window frame
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.Tool  # Not shown in taskbar
        )
        
        # Set window to be transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set stylesheet for the window
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.85);
                border-radius: 10px;
            }
            
            QPushButton {
                background-color: rgba(70, 70, 70, 0.9);
                color: white;
                border-radius: 4px;
                padding: 6px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 0.9);
            }
            
            QComboBox {
                background-color: rgba(40, 40, 40, 0.9);
                color: white;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
    def toggle_visibility(self):
        """Toggle the visibility of the window"""
        if self.is_visible:
            self.hide()
            self.is_visible = False
            logger.info("Window hidden")
        else:
            # Make sure we're using the right transparency level
            self._adjust_transparency(self.is_screen_sharing)
            self.show()
            self.is_visible = True
            self.activateWindow()  # Bring to foreground
            logger.info("Window shown")
            
    def on_screen_sharing_change(self, is_sharing):
        """
        Handle screen sharing state changes
        
        Args:
            is_sharing (bool): True if screen sharing is active
        """
        if is_sharing != self.is_screen_sharing:
            self.is_screen_sharing = is_sharing
            self._adjust_transparency(is_sharing)
            
            # Update the indicator
            self.sharing_indicator.setText(f"Screen Sharing: {'On' if is_sharing else 'Off'}")
            self.sharing_indicator.setStyleSheet(f"color: {'red' if is_sharing else 'green'};")
            
            logger.info(f"Screen sharing state changed: {is_sharing}")
            
    def _adjust_transparency(self, is_sharing):
        """
        Adjust window transparency based on screen sharing state
        
        Args:
            is_sharing (bool): True if screen sharing is active
        """
        if is_sharing:
            # When screen sharing, make the window more transparent
            # and use special window attributes to avoid capture
            self.setWindowOpacity(0.85)
            
            # Apply platform-specific screen sharing invisibility techniques
            if platform.system() == "Windows":
                self._apply_windows_invisibility(True)
            elif platform.system() == "Darwin":  # macOS
                # In macOS, apply specific techniques if we add them in the future
                self._apply_macos_invisibility(True)
            else:
                # In non-Windows/macOS (Linux/development), just make it more transparent
                self.setWindowOpacity(0.75)
        else:
            # When not screen sharing, use normal transparency
            self.setWindowOpacity(0.95)
            
            # Remove platform-specific screen capture invisibility
            if platform.system() == "Windows":
                self._apply_windows_invisibility(False)
            elif platform.system() == "Darwin":  # macOS
                self._apply_macos_invisibility(False)
                
    def _apply_windows_invisibility(self, enable):
        """
        Apply Windows-specific screen sharing invisibility techniques
        
        Args:
            enable (bool): True to enable invisibility, False to disable
        """
        try:
            hwnd = int(self.winId())
            import ctypes
            
            # Windows Desktop Window Manager API
            dwm = ctypes.WinDLL("dwmapi")
            
            # Set window as layered and transparent for screen capture
            DWMWA_CLOAK = 13  # DWM cloak value
            value = ctypes.c_int(1 if enable else 0)
            dwm.DwmSetWindowAttribute(hwnd, DWMWA_CLOAK, ctypes.byref(value), ctypes.sizeof(value))
            
            # Additional Windows invisibility techniques can be added here
            
            logger.info(f"Applied Windows invisibility: {enable}")
        except Exception as e:
            logger.error(f"Failed to apply Windows invisibility ({enable}): {str(e)}")
            
    def _apply_macos_invisibility(self, enable):
        """
        Apply macOS-specific screen sharing invisibility techniques
        
        Args:
            enable (bool): True to enable invisibility, False to disable
        """
        try:
            # Import macOS specific libraries
            import objc
            from Foundation import NSObject, NSAppleScript
            
            # On macOS, we can use the following techniques:
            # 1. Set the window layer to be excluded from screen capture
            # 2. Use the CGWindowLevel API to position window in a capture-free layer
            
            if enable:
                # Technique 1: Use NSWindow.sharingType = NSWindowSharingNone
                # We need to access the underlying NSWindow
                win_id = self.winId()
                
                # AppleScript to set sharing type
                script_text = f"""
                tell application "System Events"
                    set frontWindow to first window of (first application process whose frontmost is true)
                    set asProperty to value of attribute "AXWindowSharesVideoContent" of frontWindow to false
                end tell
                """
                
                script = NSAppleScript.alloc().initWithSource_(script_text)
                script.executeAndReturnError_(None)
                
                # Technique 2: Set window level to avoid capture
                # Uses PyObjC to call native macOS APIs
                from Cocoa import NSWindow
                
                # Get the NSWindow from our QWidget
                ns_window = objc.objc_object(c_void_p=int(win_id))
                
                # Set the window's sharingType property
                ns_window.setSharingType_(0)  # NSWindowSharingNone
                
                # Set a window level that's not captured
                ns_window.setLevel_(NSWindow.kCGHIDEventTap + 1)
                
                logger.info(f"Applied macOS invisibility techniques")
            else:
                # Restore normal window properties
                # Use AppleScript to reset sharing type
                script_text = f"""
                tell application "System Events"
                    set frontWindow to first window of (first application process whose frontmost is true)
                    set asProperty to value of attribute "AXWindowSharesVideoContent" of frontWindow to true
                end tell
                """
                
                script = NSAppleScript.alloc().initWithSource_(script_text)
                script.executeAndReturnError_(None)
                
                # Reset window level using PyObjC
                from Cocoa import NSWindow
                
                # Get the NSWindow from our QWidget
                ns_window = objc.objc_object(c_void_p=int(self.winId()))
                
                # Reset sharing type
                ns_window.setSharingType_(1)  # NSWindowSharingReadOnly
                
                # Reset window level
                ns_window.setLevel_(NSWindow.kCGNormalWindowLevel)
                
                logger.info(f"Disabled macOS invisibility techniques")
                
        except ImportError:
            # If PyObjC libraries aren't available, use fallback
            logger.warning("PyObjC not available for macOS window invisibility")
            self._apply_macos_invisibility_fallback(enable)
        except Exception as e:
            logger.error(f"Failed to apply macOS invisibility ({enable}): {str(e)}")
            self._apply_macos_invisibility_fallback(enable)
    
    def _apply_macos_invisibility_fallback(self, enable):
        """Fallback method for macOS screen sharing invisibility when PyObjC isn't available"""
        try:
            # Fallback to using subprocess to run AppleScript commands
            import subprocess
            
            if enable:
                # Make window more transparent during screen sharing
                self.setWindowOpacity(0.65)
                
                # Try to use Apple Script to modify window properties
                cmd = """
                osascript -e '
                tell application "System Events" 
                    set frontApp to first application process whose frontmost is true
                    set frontWindow to first window of frontApp
                    set value of attribute "AXWindowSharesVideoContent" of frontWindow to false
                end tell'
                """
                subprocess.run(cmd, shell=True)
                
                logger.info("Applied macOS invisibility fallback technique")
            else:
                # Restore normal transparency
                self.setWindowOpacity(0.95)
                
                # Reset window sharing property
                cmd = """
                osascript -e '
                tell application "System Events" 
                    set frontApp to first application process whose frontmost is true
                    set frontWindow to first window of frontApp
                    set value of attribute "AXWindowSharesVideoContent" of frontWindow to true
                end tell'
                """
                subprocess.run(cmd, shell=True)
                
                logger.info("Disabled macOS invisibility fallback technique")
        except Exception as e:
            logger.error(f"Failed to apply macOS invisibility fallback ({enable}): {str(e)}")
            # Ultimate fallback - just adjust opacity
            self.setWindowOpacity(0.65 if enable else 0.95)
                    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging the window"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging the window"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def get_ai_help(self):
        """Get AI help for the current problem"""
        try:
            problem = self.problem_input.toPlainText().strip()
            code = self.code_input.toPlainText().strip()
            language = self.language_selector.currentText()
            
            if not problem:
                self.response_output.setPlainText("Please enter a problem description.")
                return
                
            self.status_label.setText("Processing...")
            self.response_output.setPlainText("Getting AI assistance...")
            
            # Get AI response in a separate thread to avoid UI freezing
            import threading
            
            def get_response():
                response = self.ai_assistant.get_coding_assistance(problem, code, language)
                
                # Update UI from the main thread
                QApplication.instance().postEvent(
                    self,
                    UpdateResponseEvent(response)
                )
                
            threading.Thread(target=get_response, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Error getting AI help: {str(e)}"
            logger.error(error_msg)
            self.response_output.setPlainText(f"Error: {error_msg}")
            self.status_label.setText("Error")
            
    def analyze_code(self):
        """Analyze the current code using AI"""
        try:
            code = self.code_input.toPlainText().strip()
            language = self.language_selector.currentText()
            
            if not code:
                self.response_output.setPlainText("Please enter some code to analyze.")
                return
                
            self.status_label.setText("Analyzing...")
            self.response_output.setPlainText("Analyzing code...")
            
            # Get AI response in a separate thread to avoid UI freezing
            import threading
            
            def get_analysis():
                response = self.ai_assistant.analyze_code(code, language)
                
                # Update UI from the main thread
                QApplication.instance().postEvent(
                    self,
                    UpdateResponseEvent(response)
                )
                
            threading.Thread(target=get_analysis, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Error analyzing code: {str(e)}"
            logger.error(error_msg)
            self.response_output.setPlainText(f"Error: {error_msg}")
            self.status_label.setText("Error")
            
    def clear_inputs(self):
        """Clear all input fields"""
        self.problem_input.clear()
        self.code_input.clear()
        self.response_output.clear()
        self.status_label.setText("Ready")
    
    def get_macos_advice(self):
        """Get macOS-specific advice for the current problem"""
        # Only available on macOS
        if platform.system() != "Darwin":
            self.response_output.setPlainText("macOS specific advice is only available on macOS systems.")
            return
            
        try:
            problem = self.problem_input.toPlainText().strip()
            language = self.language_selector.currentText()
            
            if not problem:
                self.response_output.setPlainText("Please enter a problem description.")
                return
                
            self.status_label.setText("Getting macOS tips...")
            self.response_output.setPlainText("Fetching macOS-specific advice...")
            
            # Get AI response in a separate thread to avoid UI freezing
            import threading
            
            def get_macos_tips():
                response = self.ai_assistant.get_macos_advice(problem, language)
                
                # Update UI from the main thread
                QApplication.instance().postEvent(
                    self,
                    UpdateResponseEvent(response)
                )
                
            threading.Thread(target=get_macos_tips, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Error getting macOS advice: {str(e)}"
            logger.error(error_msg)
            self.response_output.setPlainText(f"Error: {error_msg}")
            self.status_label.setText("Error")
        
    def _toggle_simulated_sharing(self, checked):
        """
        Toggle simulated screen sharing mode (for development only)
        
        Args:
            checked (bool): True if checkbox is checked
        """
        if not platform.system() == "Windows":
            # Only available in development mode
            self.screen_detector.simulated_sharing = checked
            self.on_screen_sharing_change(checked)
            logger.info(f"Simulated screen sharing set to: {checked}")

    def update_response(self, response):
        """Update the response output with AI response"""
        self.response_output.setPlainText(response)
        self.status_label.setText("Ready")
        
    def event(self, event):
        """Handle custom events"""
        if HAS_PYQT and isinstance(event, UpdateResponseEvent):
            self.update_response(event.response)
            return True
        
        # Pass other events to parent class
        return super().event(event) if HAS_PYQT else True


# Custom event for updating the response from a background thread
# The QEvent import has already been handled in the imports section

class UpdateResponseEvent(QEvent):
    """Custom event for updating the response from a background thread"""
    
    if HAS_PYQT:
        EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    else:
        # Dummy value for environments without PyQt
        EVENT_TYPE = 9999
    
    def __init__(self, response):
        if HAS_PYQT:
            super().__init__(self.EVENT_TYPE)
        else:
            # Skip initialization in environments without PyQt
            pass
        self.response = response

# Only define the event handling mechanism if PyQt/PySide is available
# We'll use a more direct approach by attaching the event handler to the TransparentWindow class
# This way we avoid modifying the QWidget class directly

# The actual event handling will be implemented in the TransparentWindow class
# See the event method in the TransparentWindow class
