"""
Caching and API usage tracking utilities.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("openai_poem.cache")

class APIUsageTracker:
    """
    Tracks OpenAI API usage for monitoring and cost control.
    """
    
    def __init__(self, usage_file=None):
        """
        Initialize API usage tracker.
        
        Args:
            usage_file (str, optional): Path to usage tracking file. 
                                       Defaults to ~/.openai_poem/usage.json
        """
        if usage_file is None:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".openai_poem")
            os.makedirs(app_dir, exist_ok=True)
            usage_file = os.path.join(app_dir, "usage.json")
        
        self.usage_file = usage_file
        self._ensure_usage_file()
        
        logger.debug(f"API usage tracker initialized with file: {usage_file}")
    
    def _ensure_usage_file(self):
        """Ensure usage file exists with proper structure."""
        if not os.path.exists(self.usage_file):
            initial_data = {
                "total_requests": 0,
                "total_tokens": 0,
                "requests_by_date": {},
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.usage_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            
            logger.debug(f"Created new usage file at {self.usage_file}")
    
    def track_request(self, model, prompt_tokens, completion_tokens=None, success=True):
        """
        Track an API request.
        
        Args:
            model (str): Model used for the request
            prompt_tokens (int): Number of tokens in the prompt
            completion_tokens (int, optional): Number of tokens in the completion
            success (bool, optional): Whether the request was successful
        """
        try:
            # Load current usage data
            with open(self.usage_file, 'r') as f:
                usage_data = json.load(f)
            
            # Update total requests
            usage_data["total_requests"] += 1
            
            # Calculate total tokens
            total_tokens = prompt_tokens
            if completion_tokens is not None:
                total_tokens += completion_tokens
            
            usage_data["total_tokens"] += total_tokens
            
            # Update requests by date
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in usage_data["requests_by_date"]:
                usage_data["requests_by_date"][today] = {
                    "requests": 0,
                    "tokens": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "models": {}
                }
            
            usage_data["requests_by_date"][today]["requests"] += 1
            usage_data["requests_by_date"][today]["tokens"] += total_tokens
            
            if success:
                usage_data["requests_by_date"][today]["successful_requests"] += 1
            else:
                usage_data["requests_by_date"][today]["failed_requests"] += 1
            
            # Update model-specific stats
            if model not in usage_data["requests_by_date"][today]["models"]:
                usage_data["requests_by_date"][today]["models"][model] = {
                    "requests": 0,
                    "tokens": 0
                }
            
            usage_data["requests_by_date"][today]["models"][model]["requests"] += 1
            usage_data["requests_by_date"][today]["models"][model]["tokens"] += total_tokens
            
            # Update last updated timestamp
            usage_data["last_updated"] = datetime.now().isoformat()
            
            # Save updated usage data
            with open(self.usage_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
            
            logger.debug(f"Tracked API request: {model}, {total_tokens} tokens, success={success}")
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {str(e)}")
    
    def get_usage_summary(self):
        """
        Get a summary of API usage.
        
        Returns:
            dict: Usage summary
        """
        try:
            with open(self.usage_file, 'r') as f:
                usage_data = json.load(f)
            
            return usage_data
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {str(e)}")
            return None


class ResponseCache:
    """
    Cache for OpenAI API responses to reduce API calls and costs.
    """
    
    def __init__(self, cache_dir=None, ttl=86400):  # Default TTL: 1 day
        """
        Initialize response cache.
        
        Args:
            cache_dir (str, optional): Directory for cache files.
                                      Defaults to ~/.openai_poem/cache
            ttl (int, optional): Time-to-live for cache entries in seconds.
                                Defaults to 86400 (1 day).
        """
        if cache_dir is None:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".openai_poem")
            cache_dir = os.path.join(app_dir, "cache")
        
        self.cache_dir = cache_dir
        self.ttl = ttl
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.debug(f"Response cache initialized with directory: {cache_dir}, TTL: {ttl}s")
    
    def _get_cache_key(self, model, system_prompt, user_prompt, temperature, max_tokens):
        """
        Generate a cache key from request parameters.
        
        Args:
            model (str): Model name
            system_prompt (str): System prompt
            user_prompt (str): User prompt
            temperature (float): Temperature parameter
            max_tokens (int): Maximum tokens parameter
            
        Returns:
            str: Cache key
        """
        # Create a string representation of the request
        request_str = f"{model}|{system_prompt}|{user_prompt}|{temperature}|{max_tokens}"
        
        # Use a hash of the request string as the cache key
        import hashlib
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """
        Get the path to a cache file.
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            str: Path to cache file
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, model, system_prompt, user_prompt, temperature, max_tokens):
        """
        Get a cached response if available and not expired.
        
        Args:
            model (str): Model name
            system_prompt (str): System prompt
            user_prompt (str): User prompt
            temperature (float): Temperature parameter
            max_tokens (int): Maximum tokens parameter
            
        Returns:
            str or None: Cached response text if available, None otherwise
        """
        cache_key = self._get_cache_key(model, system_prompt, user_prompt, temperature, max_tokens)
        cache_file = self._get_cache_file(cache_key)
        
        if not os.path.exists(cache_file):
            logger.debug(f"Cache miss: {cache_key}")
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache entry has expired
            cache_time = cache_data.get("timestamp", 0)
            current_time = time.time()
            
            if current_time - cache_time > self.ttl:
                logger.debug(f"Cache expired: {cache_key}")
                return None
            
            logger.info(f"Cache hit: {cache_key}")
            return cache_data.get("response")
            
        except Exception as e:
            logger.error(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, model, system_prompt, user_prompt, temperature, max_tokens, response):
        """
        Cache a response.
        
        Args:
            model (str): Model name
            system_prompt (str): System prompt
            user_prompt (str): User prompt
            temperature (float): Temperature parameter
            max_tokens (int): Maximum tokens parameter
            response (str): Response text to cache
        """
        cache_key = self._get_cache_key(model, system_prompt, user_prompt, temperature, max_tokens)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            cache_data = {
                "timestamp": time.time(),
                "model": model,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response": response
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached response: {cache_key}")
            
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")
    
    def clear(self, max_age=None):
        """
        Clear expired cache entries.
        
        Args:
            max_age (int, optional): Maximum age of cache entries to keep in seconds.
                                    If None, uses the instance TTL.
        
        Returns:
            int: Number of cache entries cleared
        """
        if max_age is None:
            max_age = self.ttl
        
        cleared_count = 0
        current_time = time.time()
        
        try:
            for cache_file in Path(self.cache_dir).glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    cache_time = cache_data.get("timestamp", 0)
                    
                    if current_time - cache_time > max_age:
                        os.remove(cache_file)
                        cleared_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing cache file {cache_file}: {str(e)}")
            
            logger.info(f"Cleared {cleared_count} expired cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return 0
