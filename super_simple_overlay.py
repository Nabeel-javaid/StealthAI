#!/usr/bin/env python3
"""
Super Simple Overlay - An extremely simplified version for testing
This version removes any potential problematic code that might cause hanging
"""
import sys
import os
import platform
import time
import subprocess
import tempfile
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False
    print("PyQt5 is not installed. Please install with: pip install PyQt5")
    sys.exit(1)

class BasicWindow(QMainWindow):
    """A super simple window with minimal functionality"""
    
    def __init__(self):
        super().__init__()
        
        # Set basic window properties - no fancy transparency
        self.setWindowTitle("Overlay Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        
        # Add a header
        header = QLabel("Test Overlay")
        header.setFont(QFont("Arial", 16))
        layout.addWidget(header)
        
        # Add a simple button
        self.capture_btn = QPushButton("Take Screenshot")
        self.capture_btn.clicked.connect(self.on_capture)
        layout.addWidget(self.capture_btn)
        
        # Test status display
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setPlainText("Window created successfully. Click the button to test screenshot.")
        layout.addWidget(self.status)
        
        # Add a close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def on_capture(self):
        """Handle capture button click"""
        try:
            self.status.setPlainText("Taking screenshot...")
            self.hide()  # Hide window before capture
            
            # Short pause
            time.sleep(0.5)
            
            # For macOS only
            if platform.system() == "Darwin":
                # Take screenshot using screencapture
                temp_file = os.path.join(tempfile.gettempdir(), f"test_capture_{int(time.time())}.png")
                subprocess.run(["screencapture", "-x", temp_file], check=True)
                
                # Show result
                self.status.setPlainText(f"Screenshot saved to:\n{temp_file}")
            else:
                self.status.setPlainText("Screenshots are only supported on macOS")
            
            # Show window again
            self.show()
            
        except Exception as e:
            self.show()
            self.status.setPlainText(f"Error: {str(e)}")

def main():
    """Main entry point"""
    # Simple error handling
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Set attribute to avoid potential input method issues
        if hasattr(Qt, 'AA_DisableShortcutActivation'):
            app.setAttribute(Qt.AA_DisableShortcutActivation)
            
        # Create and show window without transparency
        window = BasicWindow()
        window.show()
        
        print("Window should now be visible")
        
        # Start event loop with timeout
        # Note: exec_() will block until window is closed
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())