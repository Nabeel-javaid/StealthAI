#!/usr/bin/env python3
"""
Universal Capture and Analysis Tool

This tool works anywhere - it analyzes an existing image file with OpenAI.
Perfect for situations where you can't capture the screen directly but have
an image saved somewhere.
"""
import os
import sys
import base64
import argparse
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI package not installed. Install with 'pip install openai'")
    sys.exit(1)

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

def analyze_image(image_path, prompt=None, api_key=None):
    """
    Analyze image with OpenAI Vision
    
    Args:
        image_path (str): Path to image file
        prompt (str, optional): Specific prompt for analysis
        api_key (str, optional): OpenAI API key
        
    Returns:
        str: Analysis result
    """
    # Check API key
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: No OpenAI API key provided")
            return None
    
    # Use default prompt if none provided
    if not prompt:
        prompt = "Analyze this image in detail. If it contains a coding problem or interview question, provide a complete solution with explanations."
    
    # Encode image
    base64_image = encode_image(image_path)
    if not base64_image:
        return None
    
    # Call OpenAI API
    try:
        client = OpenAI(api_key=api_key)
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
        print(f"Error calling OpenAI API: {e}")
        return None

def save_result(result, image_path, output_dir=None):
    """
    Save analysis result to file
    
    Args:
        result (str): Analysis result
        image_path (str): Path to original image
        output_dir (str, optional): Directory to save result
        
    Returns:
        str: Path to saved result
    """
    if not output_dir:
        output_dir = os.path.dirname(image_path) or os.getcwd()
    
    # Generate result filename based on image name
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"{base_name}_analysis_{timestamp}.txt"
    result_path = os.path.join(output_dir, result_filename)
    
    # Save the result
    with open(result_path, "w") as f:
        f.write(result)
    
    print(f"Result saved to: {result_path}")
    
    # Also create a HTML file that's easy to view
    html_path = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.html")
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
        .image {{ max-width: 100%; margin: 20px 0; border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <h1>Analysis Result</h1>
    <div class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    <img src="file://{os.path.abspath(image_path)}" class="image" alt="Analyzed Image">
    <h2>OpenAI Analysis:</h2>
    <pre>{result}</pre>
</body>
</html>
""")
    
    print(f"HTML result saved to: {html_path}")
    return result_path

def main():
    """Main function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Analyze an image with OpenAI Vision")
    parser.add_argument("image_path", help="Path to the image file to analyze")
    parser.add_argument("--prompt", "-p", help="Specific prompt for analysis")
    parser.add_argument("--api-key", "-k", help="OpenAI API key (if not set in environment)")
    parser.add_argument("--output-dir", "-o", help="Directory to save results")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if image exists
    if not os.path.isfile(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return 1
    
    # Analyze image
    print(f"Analyzing image: {args.image_path}")
    result = analyze_image(args.image_path, args.prompt, args.api_key)
    
    if not result:
        print("Analysis failed")
        return 1
    
    # Save result
    save_result(result, args.image_path, args.output_dir)
    
    # Print result
    print("\nAnalysis Result:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())