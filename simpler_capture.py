#!/usr/bin/env python3
"""
Very simple screen capture and analysis script without PyQt
This avoids all the GUI-related issues while still providing the core functionality
"""
import os
import sys
import time
import base64
import tempfile
import subprocess
from datetime import datetime

# Import OpenAI only if needed for API analysis
try:
    import openai
except ImportError:
    print("Warning: openai module not found. You won't be able to analyze captures.")
    print("To install: pip install openai")

def capture_screen():
    """Capture screen using macOS native screencapture utility"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.gettempdir()
    screenshot_path = os.path.join(temp_dir, f"screen_{timestamp}.png")
    
    # Take screenshot
    print("Taking screenshot...")
    subprocess.run(["screencapture", "-x", screenshot_path], check=True)
    print(f"Screen captured to: {screenshot_path}")
    return screenshot_path

def encode_image(image_path):
    """Encode image as base64 for API submission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_with_openai(image_path, prompt):
    """Analyze image with OpenAI"""
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it with: export OPENAI_API_KEY='your_key_here'")
        return None
    
    # Encode image
    print("Encoding image...")
    base64_image = encode_image(image_path)
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Call the API
    try:
        print("Sending to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",  # The newest OpenAI model is "gpt-4o" 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
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
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def main():
    """Main function"""
    print("=" * 60)
    print("StealthAI - Simple Screen Capture")
    print("=" * 60)
    print("This tool captures your screen and analyzes it with OpenAI.")
    print("It runs in the terminal to avoid GUI issues.")
    
    while True:
        print("\nMain Menu:")
        print("1. Capture screen and analyze")
        print("2. Use custom prompt")
        print("3. Exit")
        
        try:
            choice = input("Enter your choice (1-3): ")
            
            if choice == "3":
                print("Exiting program.")
                break
                
            if choice == "1" or choice == "2":
                # Capture the screen
                print("\nPreparing to capture the screen in 3 seconds...")
                print("Switch to the window you want to capture.")
                for i in range(3, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)
                
                # Take the screenshot
                screenshot_path = capture_screen()
                
                # Set the prompt
                prompt = None
                if choice == "1":
                    prompt = "Analyze this coding problem or multiple choice question. If it's code, explain the solution step by step and provide working code. If it's a multiple choice question, identify the correct answer with explanation."
                else:
                    print("\nEnter your custom prompt:")
                    prompt = input("> ")
                
                # Analyze the image
                print("\nAnalyzing image with OpenAI...")
                result = analyze_with_openai(screenshot_path, prompt)
                
                if result:
                    print("\n" + "=" * 60)
                    print("ANALYSIS RESULT:")
                    print("=" * 60)
                    print(result)
                    print("=" * 60)
                    
                    # Save result to file
                    result_path = os.path.splitext(screenshot_path)[0] + "_analysis.txt"
                    with open(result_path, "w") as f:
                        f.write(result)
                    print(f"\nAnalysis saved to: {result_path}")
                    
                    # Open the file for viewing
                    print("Opening result file...")
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", result_path], check=False)
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()