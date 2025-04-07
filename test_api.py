#!/usr/bin/env python3
"""
Test script for API functionality
This script tests if the OpenAI API can be accessed correctly
"""
import os
import sys
import logging
from ai_assistant import AIAssistant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test OpenAI API functionality"""
    print("=" * 60)
    print("AI API Test Script")
    print("=" * 60)
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not found.")
        print("Please set your API key with:")
        print("export OPENAI_API_KEY=\"your-api-key-here\"")
        return 1
    
    print(f"✅ OPENAI_API_KEY found in environment variables")
    
    # Create AI assistant
    try:
        print("Initializing AI Assistant...")
        assistant = AIAssistant()
        
        # Test basic API call
        print("\nTesting simple coding assistance API call...")
        response = assistant.get_coding_assistance(
            "Write a simple Python function to check if a string is a palindrome."
        )
        
        print("\nAPI Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        # Test macOS-specific API call
        print("\nTesting macOS-specific advice API call...")
        response = assistant.get_macos_advice(
            "How do I detect when screen sharing is active in macOS?", 
            language="Swift"
        )
        
        print("\nAPI Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during API test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())