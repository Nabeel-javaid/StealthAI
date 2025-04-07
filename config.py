"""
Configuration module for the AI coding assistant
"""
import os
import json
import logging
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration manager for the application
    """
    
    def __init__(self):
        """Initialize configuration with default values and load from file if available"""
        self.config_file = os.path.join(os.path.expanduser("~"), ".coding_assistant_config.json")
        
        # Determine default shortcut based on platform
        system = platform.system()
        if system == "Darwin":  # macOS
            default_shortcut = "ctrl+alt+c"
        else:  # Windows or Linux
            default_shortcut = "ctrl+shift+a"
            
        # Default configuration
        self.defaults = {
            "activation_shortcut": default_shortcut,
            "opacity": 0.9,
            "font_size": 12,
            "max_tokens": 1000,
            "language": "Python",
            "theme": "dark",
            "position": {
                "x": 100,
                "y": 100
            },
            "size": {
                "width": 800,
                "height": 600
            },
            "auto_save": True,
            "platform": system
        }
        
        # Current configuration (starts with defaults)
        self.current = self.defaults.copy()
        
        # Load configuration from file
        self.load()
        
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    
                    # Update current config with loaded values
                    for key, value in loaded_config.items():
                        self.current[key] = value
                        
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("No configuration file found, using defaults")
                self.save()  # Create default config file
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.current, f, indent=4)
                
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            
    def get(self, key, default=None):
        """
        Get configuration value for key
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Value for key or default
        """
        return self.current.get(key, default or self.defaults.get(key))
        
    def set(self, key, value):
        """
        Set configuration value
        
        Args:
            key (str): Configuration key
            value: Value to set
        """
        self.current[key] = value
        
        # Auto-save if enabled
        if self.get("auto_save"):
            self.save()
            
    def reset(self):
        """Reset configuration to defaults"""
        self.current = self.defaults.copy()
        self.save()
