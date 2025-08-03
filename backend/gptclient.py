"""
Core OpenAI GPT Client
Provides basic OpenAI API integration
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InvokeGPT:
    """
    Core OpenAI GPT-4o-mini Client
    Provides basic OpenAI API integration
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            api_key=api_key,
            organization=os.getenv("OPENAI_ORG_ID")  # Optional
        )
    
    def get_response(self, messages):
        """
        Generate a response to the given messages using OpenAI GPT-4o-mini
        
        Args:
            messages: List of messages in OpenAI format
            
        Returns:
            OpenAI API response object
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=False
        )
