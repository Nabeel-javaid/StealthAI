"""
AI Assistant module for providing coding help via OpenAI API
With enhanced capabilities for coding interview assistance
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
        if not IS_MACOS:
            return "This feature is only available on macOS."
            
        if not self.client:
            return "Error: OpenAI API client not initialized. Please check your API key."
            
        try:
            # Prepare the prompt with macOS specifics
            content = f"""I'm in a coding interview on macOS. Please help me with this problem:

{code_problem}

In your response, please include any macOS-specific considerations, APIs, or optimizations if relevant."""
            
            if language:
                if language.lower() in ['swift', 'objective-c']:
                    content += "\n\nPlease provide sample code using modern Swift/Objective-C best practices and Apple's recommended APIs."
                    
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert Apple platform developer familiar with macOS, Swift, Objective-C, and macOS-specific optimization techniques. Help the user with their coding interview question, providing macOS-specific insights when relevant."},
                    {"role": "user", "content": content}
                ],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Error getting macOS advice: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
