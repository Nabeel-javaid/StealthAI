#!/usr/bin/env python3
"""
Simple Overlay - A simplified version of the stealth overlay without advanced invisibility tricks

This provides the same functionality but is easier to test as it doesn't 
use the advanced macOS-specific window level tricks that might be causing issues.
"""
import sys
import os
import platform
import base64
import tempfile
import logging
import subprocess
import threading
from datetime import datetime

# Import PyQt5 components for UI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QMainWindow,
    QProgressBar, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont

# Import OpenAI for screen analysis
import openai

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenCapture:
    """Simple screen capture utility"""
    
    def __init__(self):
        """Initialize screen capture module"""
        self.temp_dir = tempfile.gettempdir()
        self.is_macos = platform.system() == "Darwin"
        
    def capture_screen(self):
        """Capture the screen using macOS native commands"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.temp_dir, f"screen_{timestamp}.png")
        
        if self.is_macos:
            # macOS-specific screen capture using screencapture utility
            subprocess.run(["screencapture", "-x", screenshot_path], check=True)
        else:
            # Fallback for non-macOS platforms (just for testing)
            raise NotImplementedError("Screen capture only implemented for macOS")
            
        logger.info(f"Screen captured to: {screenshot_path}")
        return screenshot_path
        
    def encode_image(self, image_path):
        """Convert image to base64 for API submission"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

class AnalysisWorker(QThread):
    """Background worker for screen analysis with OpenAI"""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_path, prompt=None):
        """Initialize with image and optional prompt"""
        super().__init__()
        self.image_path = image_path
        self.prompt = prompt or "Analyze this coding problem or multiple choice question. Provide the solution with detailed explanation."
        
    def run(self):
        """Process the image with OpenAI"""
        try:
            # Encode the image
            with open(self.image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Call the API
            response = client.chat.completions.create(
                model="gpt-4o",  # The newest OpenAI model is "gpt-4o" which was released May, 2024
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": self.prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            # Return the response
            self.finished.emit(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            self.error.emit(f"Error analyzing image: {str(e)}")

class SimpleOverlay(QMainWindow):
    """Simple overlay window for testing"""
    
    def __init__(self):
        """Initialize the overlay window"""
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("Simple Overlay")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Stay on top but remain visible in screen sharing
        
        # Load prompt templates
        self.prompt_templates = {
            "Coding Problem": "Analyze this coding problem. Identify the task, provide a detailed step-by-step solution, and include working code with explanations.",
            "Multiple Choice": "Analyze this multiple choice question. Identify the correct answer and explain why it's correct and why the other options are incorrect.",
            "Debugging": "Debug this code. Identify any errors, explain why they're happening, and provide fixed code.",
            "Algorithm Design": "Analyze this algorithm problem. Explain the optimal approach, the time and space complexity, and provide a complete implementation."
        }
        
        # Create UI components
        self._create_ui()
        
        # Initialize screen capture
        self.screen_capture = ScreenCapture()
        
        # Setup dragging vars
        self.dragging = False
        self.drag_position = None
        
        # Position window in the top-right corner
        screen = QApplication.primaryScreen().geometry()
        self.resize(400, 600)
        self.move(screen.width() - self.width() - 20, 100)
    
    def _create_ui(self):
        """Create the user interface components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set background color
        palette = central_widget.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        central_widget.setPalette(palette)
        central_widget.setAutoFillBackground(True)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("Simple Overlay")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Use this tool during coding interviews.\nCapture your screen to analyze problems or questions.")
        layout.addWidget(desc_label)
        
        # Prompt selection
        prompt_layout = QHBoxLayout()
        prompt_label = QLabel("Analyze as:")
        self.prompt_combo = QComboBox()
        for template_name in self.prompt_templates:
            self.prompt_combo.addItem(template_name)
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(self.prompt_combo)
        layout.addLayout(prompt_layout)
        
        # Capture button
        self.capture_button = QPushButton("Capture Screen & Analyze")
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.capture_button.clicked.connect(self.on_capture_clicked)
        layout.addWidget(self.capture_button)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(300)
        layout.addWidget(self.results_text)
        
        # Controls row
        controls_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        controls_layout.addWidget(self.clear_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        controls_layout.addWidget(self.close_button)
        
        layout.addLayout(controls_layout)
    
    def on_capture_clicked(self):
        """Handle the capture button click"""
        # Temporarily hide the window during capture
        self.hide()
        
        # Short delay to ensure the window is hidden before capture
        QTimer.singleShot(500, self._perform_capture)
    
    def _perform_capture(self):
        """Perform the actual screen capture and analysis"""
        try:
            # Show loading UI
            self.progress_bar.setVisible(True)
            self.capture_button.setEnabled(False)
            self.capture_button.setText("Analyzing...")
            self.show()  # Show window again after capture
            
            # Capture the screen
            screenshot_path = self.screen_capture.capture_screen()
            
            # Get selected prompt template
            prompt_name = self.prompt_combo.currentText()
            prompt = self.prompt_templates.get(prompt_name)
            
            # Start analysis in background thread
            self.analysis_worker = AnalysisWorker(screenshot_path, prompt)
            self.analysis_worker.finished.connect(self.on_analysis_complete)
            self.analysis_worker.error.connect(self.on_analysis_error)
            self.analysis_worker.start()
            
        except Exception as e:
            self.on_analysis_error(f"Error during capture: {str(e)}")
    
    def on_analysis_complete(self, result):
        """Handle successful analysis completion"""
        # Reset UI
        self.progress_bar.setVisible(False)
        self.capture_button.setEnabled(True)
        self.capture_button.setText("Capture Screen & Analyze")
        
        # Display result
        self.results_text.setPlainText(result)
    
    def on_analysis_error(self, error_message):
        """Handle analysis errors"""
        # Reset UI
        self.progress_bar.setVisible(False)
        self.capture_button.setEnabled(True)
        self.capture_button.setText("Capture Screen & Analyze")
        
        # Display error
        self.results_text.setPlainText(f"ERROR: {error_message}\n\nPlease make sure you have set your OpenAI API key.")
    
    def on_clear_clicked(self):
        """Clear the results area"""
        self.results_text.clear()
    
    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for window dragging"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()


def main():
    """Main entry point"""
    try:
        # Check for OpenAI API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY environment variable not found.")
            print("You will need to set this for screen analysis to work.")
            print("Run: export OPENAI_API_KEY='your-api-key'")
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create and show window
        window = SimpleOverlay()
        window.show()
        
        # Start event loop
        return app.exec_()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())