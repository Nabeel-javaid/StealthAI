#!/usr/bin/env python3
"""
Simpler Screen Capture & Analysis Tool

This is a minimalist version that works reliably on macOS without
GUI dependencies. It captures the screen using the built-in screencapture
utility and sends it to OpenAI for analysis.
"""
import os
import sys
import base64
import tempfile
import subprocess
from datetime import datetime

# Check for OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not set in environment.")
    print("Please set it with: export OPENAI_API_KEY='your-api-key'")
    sys.exit(1)

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    print("Error: OpenAI package not installed. Install with 'pip install openai'")
    sys.exit(1)

def capture_screen():
    """
    Capture the screen using macOS screencapture utility
    
    Returns:
        str: Path to the captured screenshot
    """
    # Create a temporary file for the screenshot
    fd, screenshot_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    
    try:
        # Use the screencapture utility
        print("Capturing screen in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            subprocess.run(["sleep", "1"], check=True)
        
        print("Capturing...")
        subprocess.run(["screencapture", screenshot_path], check=True)
        print(f"Screenshot saved to: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error capturing screen: {e}")
        if os.path.exists(screenshot_path):
            os.unlink(screenshot_path)
        return None

def encode_image(image_path):
    """
    Encode image to base64 for API submission
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        str: Base64 encoded image
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def analyze_with_openai(image_path, prompt):
    """
    Analyze image with OpenAI Vision
    
    Args:
        image_path (str): Path to image file
        prompt (str): Prompt for analysis
        
    Returns:
        str: Analysis result
    """
    # Encode image
    base64_image = encode_image(image_path)
    if not base64_image:
        return None
    
    print("Sending to OpenAI for analysis...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o"
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
        print(f"Error analyzing with OpenAI: {e}")
        return None

def save_result(result, screenshot_path):
    """
    Save analysis result to file
    
    Args:
        result (str): Analysis result
        screenshot_path (str): Path to screenshot
        
    Returns:
        str: Path to saved result
    """
    # Create a directory for the results
    results_dir = os.path.expanduser("~/Documents/AI_Analysis")
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"analysis_{timestamp}.txt"
    result_path = os.path.join(results_dir, result_filename)
    
    # Save the screenshot to the results directory
    screenshot_dest = os.path.join(results_dir, f"screenshot_{timestamp}.png")
    subprocess.run(["cp", screenshot_path, screenshot_dest], check=True)
    
    # Save the result
    with open(result_path, "w") as f:
        f.write(result)
    
    print(f"Screenshot saved to: {screenshot_dest}")
    print(f"Analysis saved to: {result_path}")
    
    # Also create a HTML file that's easy to view
    html_path = os.path.join(results_dir, f"analysis_{timestamp}.html")
    with open(html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Analysis Result</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .timestamp {{ color: #777; margin-bottom: 20px; }}
        .image {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <h1>AI Analysis Result</h1>
    <div class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    <img src="file://{os.path.abspath(screenshot_dest)}" class="image" alt="Screenshot">
    <h2>Analysis:</h2>
    <pre>{result}</pre>
</body>
</html>
""")
    
    print(f"HTML result saved to: {html_path}")
    return result_path

def main():
    """Main function for the application"""
    print("==== Simple Screen Capture & Analysis Tool ====")
    print("This tool captures your screen and analyzes it with OpenAI.")
    print("Results are saved to ~/Documents/AI_Analysis/")
    print("\nChoose analysis type:")
    print("1. Coding Problem (analyze code and provide solution)")
    print("2. Multiple Choice (analyze question and identify correct answer)")
    print("3. Debug Code (find and fix errors in code)")
    print("4. Custom Prompt")
    
    try:
        choice = int(input("\nEnter choice (1-4): "))
        
        if choice == 1:
            prompt = "Analyze this coding problem. Identify the task, provide a detailed step-by-step solution, and include working code with explanations."
        elif choice == 2:
            prompt = "Analyze this multiple choice question. Identify the correct answer and explain why it's correct and why the other options are incorrect."
        elif choice == 3:
            prompt = "Debug this code. Identify any errors, explain why they're happening, and provide fixed code."
        elif choice == 4:
            prompt = input("Enter your custom prompt: ")
        else:
            print("Invalid choice. Using default prompt.")
            prompt = "Analyze what's shown in this screenshot and provide detailed information."
        
        # Capture the screen
        screenshot_path = capture_screen()
        if not screenshot_path:
            print("Screen capture failed. Exiting.")
            return 1
        
        # Analyze with OpenAI
        result = analyze_with_openai(screenshot_path, prompt)
        if not result:
            print("Analysis failed. Exiting.")
            return 1
        
        # Save result
        save_result(result, screenshot_path)
        
        # Display result
        print("\nAnalysis Result:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        # Clean up temporary file
        os.unlink(screenshot_path)
        
    except ValueError:
        print("Invalid input. Please enter a number.")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())