"""
AI Assistant module for providing coding help via OpenAI API
Specifically optimized for macOS with enhanced capabilities for coding interview assistance
and macOS-specific development advice for Swift, Objective-C, and Apple frameworks
"""
import os
import json
import logging
import platform
from openai import OpenAI

logger = logging.getLogger(__name__)

# Determine if we're running on macOS
IS_MACOS = platform.system() == "Darwin"

class AIAssistant:
    """
    Class to handle communication with OpenAI API and process coding questions
    """
    
    def __init__(self):
        """Initialize the AI Assistant with API credentials"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
            
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("AI Assistant initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
            
    def get_coding_assistance(self, problem_description, code=None, language=None):
        """
        Get coding assistance for the given problem
        
        Args:
            problem_description (str): Description of the coding problem
            code (str, optional): Current code if any
            language (str, optional): Programming language
            
        Returns:
            str: AI response with coding assistance
        """
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        if not self.api_key:
            return "Error: OpenAI API key not set. Please set OPENAI_API_KEY environment variable."
            
        try:
            # Prepare the prompt
            content = f"I'm in a coding interview. Please help me with this problem:\n\n{problem_description}"
            
            if code:
                content += f"\n\nHere's my current code:\n```{language or ''}\n{code}\n```"
                
            content += "\n\nPlease provide:\n1. Analysis of the problem\n2. Approach to solve it\n3. Optimized solution with time/space complexity\n4. Potential edge cases to consider"
            
            # Call OpenAI API
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert coding assistant helping with a coding interview. Provide concise, focused answers that analyze problems and suggest efficient solutions."},
                    {"role": "user", "content": content}
                ],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error getting coding assistance: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def analyze_code(self, code, language):
        """
        Analyze code for improvements, bugs, and optimizations
        
        Args:
            code (str): Code to analyze
            language (str): Programming language
            
        Returns:
            str: Analysis of the code
        """
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Analyze the given code for improvements, bugs, and optimizations."},
                    {"role": "user", "content": f"Please review this {language} code:\n```{language}\n{code}\n```\n\nProvide concise feedback on:\n1. Correctness\n2. Time and space complexity\n3. Edge cases\n4. Style and best practices\n5. Suggested improvements"}
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error analyzing code: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def get_macos_advice(self, code_problem, language=None):
        """
        Get macOS-specific advice for coding problems
        
        Args:
            code_problem (str): Description of the coding problem
            language (str, optional): Programming language
            
        Returns:
            str: macOS-specific advice
        """
        # This function is always available even if we're not on macOS
        # since this is a macOS-focused application
        
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        try:
            # Set default language to Swift if none provided
            if not language:
                language = "Swift"
                
            # Prepare system prompt with enhanced macOS knowledge
            system_prompt = """You are an expert Apple platform developer with deep knowledge of:
1. macOS architecture and frameworks (AppKit, Cocoa, Core Services)
2. Swift and SwiftUI for macOS development
3. Objective-C and legacy macOS APIs
4. macOS-specific performance optimizations and design patterns
5. Screen sharing detection and invisibility techniques on macOS
6. macOS security and permissions model
7. Apple Silicon optimizations

Provide actionable advice for the user's coding question, with a focus on modern
macOS-specific approaches. Include relevant:
- Code examples using Swift or the user's preferred language
- Apple framework recommendations
- Platform-specific considerations
- Performance best practices for macOS
"""
            
            # Prepare the user prompt with macOS specifics
            content = f"""I'm working on a macOS development problem. Please help me with this:

{code_problem}

In your response, provide:
1. A clear explanation of the macOS-specific approach
2. Sample code that follows Apple's latest best practices
3. Any platform-specific considerations or optimizations
4. Relevant Apple frameworks and APIs for macOS"""
            
            # Add language-specific additions
            if language.lower() == 'swift':
                content += "\n\nPlease use modern Swift 5.9+ and SwiftUI when appropriate, with macOS-specific components."
            elif language.lower() == 'objective-c':
                content += "\n\nPlease use modern Objective-C with ARC and the latest macOS APIs."
            elif language.lower() in ['python', 'java', 'javascript', 'typescript']:
                content += f"\n\nPlease provide recommendations for {language} libraries or frameworks that work well on macOS, as well as any macOS-specific considerations."
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error getting macOS advice: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def analyze_macos_code(self, code, language="Swift"):
        """
        Analyze macOS-specific code for improvements and best practices
        
        Args:
            code (str): Code to analyze
            language (str, optional): Programming language, defaults to Swift
            
        Returns:
            str: macOS-specific code analysis
        """
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        try:
            # Prepare system prompt for macOS code analysis
            system_prompt = """You are an expert macOS code reviewer with deep knowledge of:
1. Apple's Human Interface Guidelines and design principles
2. macOS performance optimization
3. Apple platform best practices and Swift/Objective-C idioms
4. Common security and privacy issues on macOS
5. Memory management and thread safety on Apple platforms
6. Screen sharing and window management on macOS

Analyze the provided code specifically for macOS best practices and provide actionable advice."""
            
            # Prepare the user prompt
            content = f"""Please review this {language} code for a macOS application:

```{language}
{code}
```

Please provide a detailed analysis focusing on:
1. macOS-specific best practices and idioms
2. Performance optimizations for Apple platforms
3. Interface guideline compliance
4. Security and sandbox considerations
5. Suggested improvements for macOS compatibility"""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error analyzing macOS code: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def analyze_image(self, base64_image, prompt=None):
        """
        Analyze image content using OpenAI's multimodal capabilities
        
        Args:
            base64_image (str): Base64 encoded image string
            prompt (str, optional): Specific instructions for the analysis
            
        Returns:
            str: AI analysis of the image content
        """
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        try:
            # Default prompt if none provided
            if not prompt:
                prompt = "Analyze this screenshot and describe what you see. If there's code visible, explain what it does."
                
            # Craft system message based on context
            system_message = """You are an expert coding assistant that can analyze screenshots.
When analyzing screenshots:
1. Describe what you see in the image
2. If there's code visible, explain what it does and suggest improvements
3. If there's an error message or log output, explain the issue and suggest solutions
4. For UI elements, describe their purpose and any design considerations
5. Be detailed but concise in your analysis"""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]}
                ],
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error analyzing image: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
