#!/usr/bin/env python3
"""
Fallback mode for CLI environments without GUI support
This script provides a simple interactive CLI interface for the AI Assistant
"""
import os
import sys
import logging
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AI Assistant
from ai_assistant import AIAssistant

def main():
    """Fallback mode with command-line interface"""
    print("=" * 60)
    print("Discreet AI Coding Assistant - CLI Fallback Mode")
    print("=" * 60)
    
    system = platform.system()
    print(f"Running on: {system}")
    
    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not found.")
        print("Please set your API key with:")
        print("export OPENAI_API_KEY=\"your-api-key-here\"")
        return 1
    
    # Initialize AI assistant
    try:
        print("Initializing AI Assistant...")
        assistant = AIAssistant()
        
        print("\nCLI Fallback Mode Ready")
        print("Enter 'exit' or 'quit' to end the session")
        print("-" * 60)
        
        while True:
            # Show menu
            print("\nOptions:")
            print("1. Get coding assistance")
            print("2. Analyze code")
            print("3. Get macOS advice")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == "1":
                # Get coding assistance
                print("\n-- Coding Assistance --")
                problem = input("Describe your coding problem: ").strip()
                
                # Optional code input
                has_code = input("Do you have existing code to include? (y/n): ").strip().lower()
                code = None
                language = None
                
                if has_code == "y":
                    print("Enter your code (type 'END' on a new line when finished):")
                    code_lines = []
                    while True:
                        line = input()
                        if line == "END":
                            break
                        code_lines.append(line)
                    
                    code = "\n".join(code_lines)
                    language = input("What programming language is this? ").strip()
                
                print("\nSending request to OpenAI API...")
                response = assistant.get_coding_assistance(problem, code, language)
                
                print("\nResponse:")
                print("-" * 60)
                print(response)
                print("-" * 60)
                
            elif choice == "2":
                # Analyze code
                print("\n-- Code Analysis --")
                print("Enter your code (type 'END' on a new line when finished):")
                
                code_lines = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    code_lines.append(line)
                
                code = "\n".join(code_lines)
                language = input("What programming language is this? ").strip()
                
                print("\nAnalyzing code...")
                response = assistant.analyze_code(code, language)
                
                print("\nAnalysis:")
                print("-" * 60)
                print(response)
                print("-" * 60)
                
            elif choice == "3":
                # Get macOS advice
                print("\n-- macOS Development Advice --")
                problem = input("Describe your macOS development question: ").strip()
                language = input("What programming language? (default: Swift): ").strip()
                
                if not language:
                    language = "Swift"
                
                print("\nGetting macOS advice...")
                response = assistant.get_macos_advice(problem, language)
                
                print("\nAdvice:")
                print("-" * 60)
                print(response)
                print("-" * 60)
                
            elif choice == "4" or choice.lower() in ["exit", "quit"]:
                print("\nExiting AI Assistant")
                break
                
            else:
                print("\nInvalid option. Please try again.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nSession interrupted by user.")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Error in fallback mode: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())