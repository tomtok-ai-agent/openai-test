"""
Client factory for creating API clients.
"""

from .openai_client import OpenAIClient

class ClientFactory:
    """
    Factory for creating API clients.
    """
    
    @staticmethod
    def create_openai_client(api_key=None, mock_client=None, use_cache=True):
        """
        Create OpenAI client.
        
        Args:
            api_key (str, optional): API key. If not provided, will be read from environment.
            mock_client (object, optional): Mock client to use instead of real client.
            use_cache (bool, optional): Whether to use response caching. Defaults to True.
            
        Returns:
            OpenAIClient: OpenAI client instance or mock
        """
        if mock_client:
            return mock_client
        
        return OpenAIClient(api_key=api_key, use_cache=use_cache)
