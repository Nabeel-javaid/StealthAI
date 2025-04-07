"""
Universal Screen Capture and Analysis Tool

This is a cross-platform version that works in any environment including Replit.
It doesn't rely on capturing the actual screen, but instead processes any image file you provide.
"""
import os
import sys
import base64
import logging
from datetime import datetime

# Import AI Assistant for API communication
from ai_assistant import AIAssistant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("UniversalCapture")

class UniversalCapture:
    """
    Handles image processing and AI analysis regardless of environment
    """
    
    def __init__(self):
        """Initialize with OpenAI integration"""
        self.ai_assistant = AIAssistant()
        
        # Check for OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Error: OpenAI API key not found in environment variables.")
            print("Please set the OPENAI_API_KEY environment variable.")
            print("Example: export OPENAI_API_KEY=your_api_key_here")
            sys.exit(1)
    
    def encode_image(self, image_path):
        """
        Encode image as base64 for API submission
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Base64 encoded image
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return None
    
    def analyze_image(self, image_path, prompt=None):
        """
        Analyze image with OpenAI
        
        Args:
            image_path (str): Path to image file
            prompt (str, optional): Additional instructions for analysis
            
        Returns:
            str: AI analysis of image content
        """
        if not os.path.exists(image_path):
            return f"Error: Image file not found at {image_path}"
            
        # Encode image
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return "Failed to encode image for analysis"
            
        # Default prompt if none provided
        if not prompt:
            prompt = "Analyze this image and describe what you see. If there's code visible, explain what it does."
            
        # Get analysis from OpenAI
        response = self.ai_assistant.analyze_image(base64_image, prompt)
        return response

def main():
    """Main function for the universal capture tool"""
    print("\n" + "="*70)
    print("Universal Image Analysis Tool")
    print("="*70)
    
    # Create the analyzer
    analyzer = UniversalCapture()
    
    # Main menu loop
    while True:
        print("\nMain Menu:")
        print("1. Analyze an image file")
        print("2. Analyze with custom prompt")
        print("3. Show example prompts")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # Analyze with default prompt
            image_path = input("\nEnter the path to the image file: ").strip()
            if not image_path:
                print("No image path provided. Returning to menu.")
                continue
                
            if not os.path.exists(image_path):
                print(f"❌ Error: File not found at {image_path}")
                continue
                
            prompt = "Analyze this image and describe what you see. If there's code visible, explain what it does."
            analyze_image(analyzer, image_path, prompt)
            
        elif choice == '2':
            # Analyze with custom prompt
            image_path = input("\nEnter the path to the image file: ").strip()
            if not image_path:
                print("No image path provided. Returning to menu.")
                continue
                
            if not os.path.exists(image_path):
                print(f"❌ Error: File not found at {image_path}")
                continue
                
            print("\nEnter your custom prompt for analysis:")
            print("Examples: 'Explain the code in this screenshot', 'Debug the error message'")
            custom_prompt = input("> ").strip()
            
            if not custom_prompt:
                print("No prompt entered. Using default prompt.")
                custom_prompt = "Analyze this image and describe what you see. If there's code visible, explain what it does."
                
            analyze_image(analyzer, image_path, custom_prompt)
            
        elif choice == '3':
            # Show example prompts
            print("\nExample prompts you can use:")
            print("- 'Analyze this code and explain what it does'")
            print("- 'Debug the error message in this screenshot'")
            print("- 'Explain the UI elements in this application'")
            print("- 'Transcribe any text visible in this image'")
            print("- 'Analyze this chart or graph and explain its meaning'")
            print("- 'Explain what's happening in this Terminal output'")
            print("- 'Help me understand the documentation shown in the image'")
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            # Exit
            print("\nThank you for using the Universal Image Analysis Tool!")
            break
            
        else:
            print("\nInvalid choice. Please enter a number from 1 to 4.")

def analyze_image(analyzer, image_path, prompt):
    """
    Analyze an image with the given prompt
    
    Args:
        analyzer (UniversalCapture): Analyzer instance
        image_path (str): Path to the image file
        prompt (str): Prompt for analysis
    """
    print("\n🔍 Analyzing image with OpenAI...")
    print("This may take a moment...")
    
    try:
        result = analyzer.analyze_image(image_path, prompt)
        
        # Print the result
        print("\n" + "="*70)
        print("ANALYSIS RESULT:")
        print("="*70)
        print(result)
        print("="*70)
        
        # Save result to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"image_analysis_{timestamp}.txt"
        
        with open(result_file, "w") as f:
            f.write(result)
        
        print(f"\n✅ Analysis saved to: {result_file}")
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        print(f"\n❌ Error analyzing image: {str(e)}")

if __name__ == "__main__":
    main()