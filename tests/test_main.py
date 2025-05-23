"""
Tests for the main module functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from openai_test.main import generate_poem, main

class TestMainModule:
    """Test suite for main module functionality."""
    
    @pytest.fixture
    def mock_client_factory(self):
        """Fixture to mock ClientFactory."""
        with patch('openai_test.main.ClientFactory') as mock_factory:
            mock_client = MagicMock()
            mock_factory.create_openai_client.return_value = mock_client
            mock_client.generate_text.return_value = "This is a mock poem about the date."
            yield mock_factory, mock_client
    
    @pytest.fixture
    def mock_get_current_date(self):
        """Fixture to mock get_current_date function."""
        with patch('openai_test.main.get_current_date') as mock_get_date:
            mock_get_date.return_value = "May 23, 2025"
            yield mock_get_date
    
    @patch('openai_test.main.validate_api_key')
    def test_generate_poem_success(self, mock_validate, mock_client_factory):
        """Test successful poem generation."""
        # Arrange
        mock_factory, mock_client = mock_client_factory
        os.environ["OPENAI_API_KEY"] = "test_key"
        mock_validate.return_value = True
        
        # Act
        result = generate_poem("May 23, 2025")
        
        # Assert
        assert result == "This is a mock poem about the date."
        mock_factory.create_openai_client.assert_called_once()
        mock_client.generate_text.assert_called_once()
    
    def test_generate_poem_no_api_key(self, mock_client_factory):
        """Test poem generation with no API key."""
        # Arrange
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Act
        result = generate_poem("May 23, 2025")
        
        # Assert
        assert "Error: OPENAI_API_KEY environment variable not set" in result
        mock_client_factory[0].create_openai_client.assert_not_called()
    
    @patch('openai_test.main.validate_api_key')
    def test_generate_poem_invalid_api_key(self, mock_validate, mock_client_factory):
        """Test poem generation with invalid API key."""
        # Arrange
        os.environ["OPENAI_API_KEY"] = "invalid_key"
        mock_validate.return_value = False
        
        # Act
        result = generate_poem("May 23, 2025")
        
        # Assert
        assert "Error: OPENAI_API_KEY has invalid format" in result
        mock_client_factory[0].create_openai_client.assert_not_called()
    
    @patch('openai_test.main.print')
    @patch('openai_test.main.parse_arguments')
    @patch('openai_test.main.validate_api_key')
    def test_main_function(self, mock_validate, mock_parse_args, mock_print, mock_client_factory, mock_get_current_date):
        """Test main function execution."""
        # Arrange
        mock_args = MagicMock()
        mock_args.date = None
        mock_args.model = "gpt-3.5-turbo"
        mock_args.temperature = 0.7
        mock_args.max_tokens = 500
        mock_args.log_level = "INFO"
        mock_args.no_cache = False
        mock_args.clear_cache = False
        mock_args.show_usage = False
        mock_parse_args.return_value = mock_args
        
        os.environ["OPENAI_API_KEY"] = "test_key"
        mock_validate.return_value = True
        
        # Act
        main()
        
        # Assert
        mock_get_current_date.assert_called_once()
        mock_client_factory[1].generate_text.assert_called_once()
        
        # Check that print was called with the poem
        any_poem_print = False
        for call in mock_print.call_args_list:
            args, _ = call
            if args and "This is a mock poem about the date." in args:
                any_poem_print = True
                break
        
        assert any_poem_print, "The poem was not printed"
