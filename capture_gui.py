"""
Screen Capture and Analysis with GUI Interface

This application provides a GUI for capturing your screen and getting AI analysis.
It's designed to be simple, intuitive, and Mac-native.
"""
import os
import sys
import time
import logging
import platform
from datetime import datetime

# Check for macOS and required packages
if platform.system() != "Darwin":
    print("Warning: This application is optimized for macOS.")
    print("Some features may not work on other platforms.")

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTextEdit, QLabel, QComboBox, QCheckBox, QMessageBox,
        QSplitter, QFrame
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
    from PyQt5.QtGui import QFont, QIcon, QTextCursor
except ImportError:
    print("Error: PyQt5 is required but not installed.")
    print("Please install it with: pip install PyQt5")
    sys.exit(1)

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
logger = logging.getLogger("CaptureGUI")

# Worker thread for background processing
class AnalysisWorker(QThread):
    """Background worker thread for screen capture and analysis"""
    finished = pyqtSignal(str)
    
    def __init__(self, screen_capture, ai_assistant, prompt=None):
        super().__init__()
        self.screen_capture = screen_capture
        self.ai_assistant = ai_assistant
        self.prompt = prompt
    
    def run(self):
        try:
            # Capture the screen
            screenshot_path = self.screen_capture.capture_screen()
            if not screenshot_path:
                self.finished.emit("Failed to capture screen. Please check permissions.")
                return
            
            # Encode the image
            base64_image = self.screen_capture.encode_image(screenshot_path)
            if not base64_image:
                self.finished.emit("Failed to encode image for analysis.")
                return
            
            # Analyze with OpenAI
            result = self.ai_assistant.analyze_image(base64_image, self.prompt)
            
            # Clean up
            self.screen_capture.clean_up()
            
            # Return the result
            self.finished.emit(result)
            
        except Exception as e:
            self.finished.emit(f"Error during analysis: {str(e)}")

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.ai_assistant = AIAssistant()
        
        # Check for OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            QMessageBox.critical(
                self, 
                "API Key Missing", 
                "OpenAI API key not found in environment variables.\n\n"
                "Please set the OPENAI_API_KEY environment variable and restart the application.\n\n"
                "Example: export OPENAI_API_KEY=your_api_key_here"
            )
            sys.exit(1)
        
        self.setWindowTitle("macOS Screen Capture & AI Analysis")
        self.setMinimumSize(800, 600)
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header = QLabel("macOS Screen Capture & AI Analysis")
        header.setFont(QFont("SF Pro Display", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Description
        description = QLabel(
            "This tool captures your screen and analyzes it with OpenAI's AI model. "
            "You can customize the prompt to get specific information from your screenshot."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Vertical)
        
        # Top section for controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Prompt selection area
        prompt_label = QLabel("Select a prompt template or write your own:")
        top_layout.addWidget(prompt_label)
        
        # Premade prompts combo box
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItems([
            "Custom prompt...",
            "Analyze this code and explain what it does",
            "Debug the error message in this screenshot",
            "Explain the UI elements in this application",
            "Transcribe any text visible in this screenshot",
            "Analyze this chart or graph and explain its meaning"
        ])
        self.prompt_combo.currentIndexChanged.connect(self.on_prompt_template_changed)
        top_layout.addWidget(self.prompt_combo)
        
        # Custom prompt text area
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Enter your custom prompt here...")
        self.prompt_text.setText("Analyze this screenshot and describe what you see. If there's code visible, explain what it does.")
        self.prompt_text.setMaximumHeight(100)
        top_layout.addWidget(self.prompt_text)
        
        # Capture controls
        controls_layout = QHBoxLayout()
        
        # Countdown option
        self.countdown_check = QCheckBox("3-second countdown")
        self.countdown_check.setChecked(True)
        controls_layout.addWidget(self.countdown_check)
        
        # Spacer
        controls_layout.addStretch()
        
        # Capture button
        self.capture_button = QPushButton("Capture Screen & Analyze")
        self.capture_button.setMinimumHeight(40)
        self.capture_button.clicked.connect(self.on_capture_clicked)
        controls_layout.addWidget(self.capture_button)
        
        top_layout.addLayout(controls_layout)
        content_splitter.addWidget(top_widget)
        
        # Bottom section for results
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        results_label = QLabel("Analysis Results:")
        bottom_layout.addWidget(results_label)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("SF Mono", 12))
        self.results_text.setPlaceholderText("Analysis results will appear here...")
        bottom_layout.addWidget(self.results_text)
        
        # Bottom controls
        bottom_controls = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("Save Analysis")
        self.save_button.clicked.connect(self.on_save_clicked)
        self.save_button.setEnabled(False)
        bottom_controls.addWidget(self.save_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        bottom_controls.addWidget(self.clear_button)
        
        bottom_layout.addLayout(bottom_controls)
        content_splitter.addWidget(bottom_widget)
        
        # Set initial splitter sizes
        content_splitter.setSizes([200, 400])
        main_layout.addWidget(content_splitter)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Progress indicator
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
    
    def on_prompt_template_changed(self, index):
        """Handle selection of prompt template"""
        if index == 0:  # "Custom prompt..."
            # Keep the current text
            return
        
        # Get the selected template text
        template_text = self.prompt_combo.currentText()
        self.prompt_text.setText(template_text)
    
    def on_capture_clicked(self):
        """Handle capture button click"""
        # Check for screen recording permissions (macOS)
        if platform.system() == "Darwin":
            # Unfortunately we can't programmatically check permissions,
            # so we'll just show a reminder
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Permission Check")
            msg.setText("This application needs screen recording permission to capture your screen.")
            msg.setInformativeText(
                "If you haven't granted permission yet, please go to:\n"
                "System Preferences > Security & Privacy > Privacy > Screen Recording\n\n"
                "Add this application to the list of allowed apps."
            )
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            if msg.exec_() == QMessageBox.Cancel:
                return
        
        # Get the prompt
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
        
        # Disable UI during capture and analysis
        self.capture_button.setEnabled(False)
        self.prompt_text.setEnabled(False)
        self.prompt_combo.setEnabled(False)
        self.countdown_check.setEnabled(False)
        
        # Handle countdown if enabled
        if self.countdown_check.isChecked():
            self.do_countdown()
        else:
            self.perform_capture(prompt)
    
    def do_countdown(self):
        """Perform countdown before capture"""
        self.countdown_seconds = 3
        self.status_label.setText(f"Capturing in {self.countdown_seconds}...")
        
        # Set up timer for countdown
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.countdown_tick)
        self.countdown_timer.start(1000)  # 1 second
    
    def countdown_tick(self):
        """Handle countdown timer tick"""
        self.countdown_seconds -= 1
        
        if self.countdown_seconds > 0:
            self.status_label.setText(f"Capturing in {self.countdown_seconds}...")
        else:
            self.countdown_timer.stop()
            self.status_label.setText("Capturing...")
            
            # Get the current prompt
            prompt = self.prompt_text.toPlainText().strip()
            if not prompt:
                prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
            
            # Perform the actual capture
            self.perform_capture(prompt)
    
    def perform_capture(self, prompt):
        """Perform the actual screen capture and analysis"""
        self.status_label.setText("Capturing screen...")
        
        # Start the worker thread
        self.worker = AnalysisWorker(self.screen_capture, self.ai_assistant, prompt)
        self.worker.finished.connect(self.on_analysis_complete)
        self.worker.start()
        
        # Update status
        self.status_label.setText("Analyzing with OpenAI...")
    
    def on_analysis_complete(self, result):
        """Handle completion of analysis"""
        # Re-enable UI
        self.capture_button.setEnabled(True)
        self.prompt_text.setEnabled(True)
        self.prompt_combo.setEnabled(True)
        self.countdown_check.setEnabled(True)
        
        # Update results
        self.results_text.setText(result)
        self.results_text.moveCursor(QTextCursor.Start)
        
        # Enable save button
        self.save_button.setEnabled(True)
        
        # Update status
        self.status_label.setText("Analysis complete")
    
    def on_save_clicked(self):
        """Handle save button click"""
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_analysis_{timestamp}.txt"
        
        try:
            # Save the analysis
            with open(filename, "w") as f:
                f.write(self.results_text.toPlainText())
            
            # Show success message
            self.status_label.setText(f"Analysis saved to {filename}")
            
            # Show dialog
            QMessageBox.information(
                self,
                "Analysis Saved",
                f"Analysis has been saved to:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Error saving analysis: {str(e)}"
            )
    
    def on_clear_clicked(self):
        """Handle clear button click"""
        self.results_text.clear()
        self.save_button.setEnabled(False)
        self.status_label.setText("Ready")

def main():
    """Main application entry point"""
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style to be native on macOS
    if platform.system() == "Darwin":
        app.setStyle("macintosh")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()