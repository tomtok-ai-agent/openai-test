"""
Tests for the OpenAI client wrapper.
"""

import pytest
from unittest.mock import patch, MagicMock
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError, BadRequestError

from openai_test.api.openai_client import OpenAIClient
from openai_test.config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class TestOpenAIClient:
    """Test suite for OpenAIClient class."""
    
    @pytest.fixture
    def mock_openai(self):
        """Fixture to mock OpenAI client."""
        with patch('openai_test.api.openai_client.OpenAI') as mock_openai:
            # Create a mock for the chat completions create method
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            # Mock response structure
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "This is a mock poem about the date."
            mock_response.usage.prompt_tokens = 50
            mock_response.usage.completion_tokens = 100
            
            # Set up the mock client to return our mock response
            mock_client.chat.completions.create.return_value = mock_response
            
            yield mock_client
    
    @pytest.fixture
    def mock_cache(self):
        """Fixture to mock ResponseCache."""
        with patch('openai_test.api.openai_client.ResponseCache') as mock_cache_class:
            mock_cache = MagicMock()
            mock_cache_class.return_value = mock_cache
            mock_cache.get.return_value = None  # Default to cache miss
            yield mock_cache
    
    @pytest.fixture
    def mock_usage_tracker(self):
        """Fixture to mock APIUsageTracker."""
        with patch('openai_test.api.openai_client.APIUsageTracker') as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker_class.return_value = mock_tracker
            mock_tracker.get_usage_summary.return_value = {
                "total_requests": 1,
                "total_tokens": 150,
                "requests_by_date": {
                    "2025-05-23": {
                        "requests": 1,
                        "tokens": 150,
                        "successful_requests": 1,
                        "failed_requests": 0
                    }
                }
            }
            yield mock_tracker
    
    def test_generate_text_success(self, mock_openai, mock_cache, mock_usage_tracker):
        """Test successful text generation."""
        # Arrange
        client = OpenAIClient(api_key="test_key")
        system_prompt = SYSTEM_PROMPT
        user_prompt = USER_PROMPT_TEMPLATE.format(date="May 23, 2025")
        
        # Act
        result = client.generate_text(system_prompt, user_prompt)
        
        # Assert
        assert result == "This is a mock poem about the date."
        mock_openai.chat.completions.create.assert_called_once()
        mock_usage_tracker.track_request.assert_called_once()
        mock_cache.set.assert_called_once()
    
    def test_generate_text_from_cache(self, mock_openai, mock_cache, mock_usage_tracker):
        """Test text generation with cache hit."""
        # Arrange
        client = OpenAIClient(api_key="test_key")
        system_prompt = SYSTEM_PROMPT
        user_prompt = USER_PROMPT_TEMPLATE.format(date="May 23, 2025")
        mock_cache.get.return_value = "This is a cached poem about the date."
        
        # Act
        result = client.generate_text(system_prompt, user_prompt)
        
        # Assert
        assert result == "This is a cached poem about the date."
        mock_openai.chat.completions.create.assert_not_called()
        mock_usage_tracker.track_request.assert_not_called()
    
    def test_generate_text_authentication_error(self, mock_openai, mock_cache, mock_usage_tracker):
        """Test handling of authentication error."""
        # Arrange
        client = OpenAIClient(api_key="invalid_key")
        system_prompt = SYSTEM_PROMPT
        user_prompt = USER_PROMPT_TEMPLATE.format(date="May 23, 2025")
        
        # Create a mock error with the required structure
        mock_error = MagicMock(spec=AuthenticationError)
        mock_error.__str__.return_value = "Invalid API key"
        mock_openai.chat.completions.create.side_effect = mock_error
        
        # Act & Assert
        with pytest.raises(Exception):  # Using generic Exception to catch our mock
            client.generate_text(system_prompt, user_prompt)
        
        mock_usage_tracker.track_request.assert_called_once()
        assert mock_usage_tracker.track_request.call_args[1]["success"] == False
    
    def test_get_usage_summary(self, mock_openai, mock_usage_tracker):
        """Test getting usage summary."""
        # Arrange
        client = OpenAIClient(api_key="test_key")
        
        # Act
        result = client.get_usage_summary()
        
        # Assert
        assert result["total_requests"] == 1
        assert result["total_tokens"] == 150
        assert "2025-05-23" in result["requests_by_date"]
    
    def test_clear_cache(self, mock_openai, mock_cache):
        """Test clearing cache."""
        # Arrange
        client = OpenAIClient(api_key="test_key")
        mock_cache.clear.return_value = 5
        
        # Act
        result = client.clear_cache()
        
        # Assert
        assert result == 5
        mock_cache.clear.assert_called_once()
