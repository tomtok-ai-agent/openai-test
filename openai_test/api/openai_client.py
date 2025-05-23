"""
OpenAI API client wrapper.
"""

import os
import logging
from openai import OpenAI
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError, BadRequestError
from ..config import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from ..utils.cache import ResponseCache, APIUsageTracker

logger = logging.getLogger("openai_poem.api")

class OpenAIClient:
    """
    Wrapper for OpenAI API client.
    """
    
    def __init__(self, api_key=None, use_cache=True, track_usage=True):
        """
        Initialize OpenAI client.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will be read from environment.
            use_cache (bool, optional): Whether to use response caching. Defaults to True.
            track_usage (bool, optional): Whether to track API usage. Defaults to True.
            
        Raises:
            ValueError: If API key is not provided and not set in environment
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("API key not provided and OPENAI_API_KEY environment variable not set")
            raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.debug("OpenAI client initialized successfully")
        
        # Initialize cache and usage tracker if enabled
        self.use_cache = use_cache
        self.track_usage = track_usage
        
        if self.use_cache:
            self.cache = ResponseCache()
            logger.debug("Response cache initialized")
        
        if self.track_usage:
            self.usage_tracker = APIUsageTracker()
            logger.debug("API usage tracker initialized")
    
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
        
        # Check cache first if enabled
        if self.use_cache:
            cached_response = self.cache.get(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if cached_response:
                logger.info("Using cached response")
                return cached_response
        
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
            
            # Cache the response if caching is enabled
            if self.use_cache:
                self.cache.set(
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response=generated_text
                )
            
            # Track API usage if tracking is enabled
            if self.track_usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    success=True
                )
            
            return generated_text
            
        except AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            raise AuthenticationError(f"Invalid API key or unauthorized access: {str(e)}")
            
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            raise RateLimitError(f"OpenAI API rate limit exceeded. Please try again later: {str(e)}")
            
        except APIConnectionError as e:
            logger.error(f"API connection error: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            raise APIConnectionError(f"Failed to connect to OpenAI API. Please check your internet connection: {str(e)}")
            
        except BadRequestError as e:
            logger.error(f"Bad request error: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            raise BadRequestError(f"Invalid request parameters: {str(e)}")
            
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            # Create a mock request object to satisfy APIError.__init__ requirements
            # This fixes the "APIError.__init__() missing 1 required positional argument: 'request'" error
            mock_request = {"method": "POST", "url": "https://api.openai.com/v1/chat/completions"}
            raise APIError(f"OpenAI API returned an error: {str(e)}", request=mock_request)
            
        except Exception as e:
            logger.error(f"Unexpected error generating text: {str(e)}")
            if self.track_usage:
                self.usage_tracker.track_request(
                    model=model,
                    prompt_tokens=len(system_prompt) + len(user_prompt),
                    success=False
                )
            raise Exception(f"An unexpected error occurred: {str(e)}")
            
    def get_usage_summary(self):
        """
        Get a summary of API usage.
        
        Returns:
            dict or None: Usage summary if tracking is enabled, None otherwise
        """
        if not self.track_usage:
            logger.warning("API usage tracking is disabled")
            return None
        
        return self.usage_tracker.get_usage_summary()
    
    def clear_cache(self, max_age=None):
        """
        Clear expired cache entries.
        
        Args:
            max_age (int, optional): Maximum age of cache entries to keep in seconds.
                                    If None, uses the default TTL.
        
        Returns:
            int or None: Number of cache entries cleared if caching is enabled, None otherwise
        """
        if not self.use_cache:
            logger.warning("Response caching is disabled")
            return None
        
        return self.cache.clear(max_age=max_age)
