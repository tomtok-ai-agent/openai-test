"""
OpenAI API client wrapper.
"""

import os
import logging
from openai import OpenAI
from ..config import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

logger = logging.getLogger("openai_poem.api")

class OpenAIClient:
    """
    Wrapper for OpenAI API client.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will be read from environment.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_text(self, system_prompt, user_prompt, model=OPENAI_MODEL, 
                     max_tokens=OPENAI_MAX_TOKENS, temperature=OPENAI_TEMPERATURE):
        """
        Generate text using OpenAI API.
        
        Args:
            system_prompt (str): System prompt for the model
            user_prompt (str): User prompt for the model
            model (str, optional): Model to use. Defaults to config value.
            max_tokens (int, optional): Maximum tokens to generate. Defaults to config value.
            temperature (float, optional): Temperature parameter. Defaults to config value.
            
        Returns:
            str: Generated text
            
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            APIConnectionError: If connection to API fails
            Exception: For other unexpected errors
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
