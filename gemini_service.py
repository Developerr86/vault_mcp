"""
Gemini Service module for the Vault 78 MCP Server.
Handles interactions with the Gemini 2.0 LLM.
"""

import os
import google.generativeai as genai
from typing import Optional

class GeminiService:
    def __init__(self):
        """
        Initialize the Gemini service with the API key.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize Gemini 2.0 model
        # Use the most capable model available
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            print(f"Warning: Could not initialize gemini-1.5-pro: {e}")
            print("Falling back to gemini-1.0-pro...")
            try:
                self.model = genai.GenerativeModel('gemini-1.0-pro')
            except Exception as e:
                print(f"Warning: Could not initialize gemini-1.0-pro: {e}")
                print("Falling back to gemini-pro...")
                self.model = genai.GenerativeModel('gemini-pro')
    
    def ask_question(self, question: str, context: Optional[str] = None) -> str:
        """
        Ask a question to the Gemini LLM.
        
        Args:
            question (str): The question to ask
            context (str, optional): Additional context to provide to the LLM
            
        Returns:
            str: The LLM's response
        """
        try:
            if context:
                prompt = f"""
                # Context Information
                
                {context}
                
                # Question
                
                Based on the above context, please answer the following question:
                {question}
                
                Provide a comprehensive and accurate answer based solely on the information in the context.
                If the context doesn't contain relevant information to answer the question, please state that.
                """
            else:
                prompt = question
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error querying Gemini: {str(e)}"
    
    def summarize_content(self, content: str) -> str:
        """
        Summarize the given content using Gemini.
        
        Args:
            content (str): The content to summarize
            
        Returns:
            str: The summarized content
        """
        try:
            prompt = f"""
            Please provide a comprehensive summary of the following content:
            
            {content}
            
            Your summary should:
            1. Capture the main topics and key points
            2. Be well-structured and organized
            3. Be concise yet informative
            4. Maintain the original meaning and intent
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error summarizing content: {str(e)}"
