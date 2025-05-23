"""
OpenAI API client wrapper.
"""

import os
import logging
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError, BadRequestError
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
            
        Raises:
            ValueError: If API key is not provided and not set in environment
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("API key not provided and OPENAI_API_KEY environment variable not set")
            raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.debug("OpenAI client initialized successfully")
    
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
            BadRequestError: If the request is invalid
            APIError: If the API returns an error
            Exception: For other unexpected errors
        """
        logger.info(f"Generating text using model: {model}")
        logger.debug(f"System prompt: {system_prompt}")
        logger.debug(f"User prompt: {user_prompt}")
        
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
            
            generated_text = response.choices[0].message.content.strip()
            logger.info("Text generated successfully")
            logger.debug(f"Generated text length: {len(generated_text)} characters")
            
            return generated_text
            
        except AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(f"Invalid API key or unauthorized access: {str(e)}")
            
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise RateLimitError(f"OpenAI API rate limit exceeded. Please try again later: {str(e)}")
            
        except APIConnectionError as e:
            logger.error(f"API connection error: {str(e)}")
            raise APIConnectionError(f"Failed to connect to OpenAI API. Please check your internet connection: {str(e)}")
            
        except BadRequestError as e:
            logger.error(f"Bad request error: {str(e)}")
            raise BadRequestError(f"Invalid request parameters: {str(e)}")
            
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise APIError(f"OpenAI API returned an error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error generating text: {str(e)}")
            raise Exception(f"An unexpected error occurred: {str(e)}")
