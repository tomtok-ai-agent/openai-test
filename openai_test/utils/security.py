"""
Security utilities for the OpenAI poem generator.
"""

def validate_api_key(api_key):
    """
    Validates the format of an OpenAI API key.
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        bool: True if the key has a valid format, False otherwise
    """
    # Basic validation checks
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Check prefix (OpenAI keys typically start with "sk-")
    if not api_key.startswith("sk-"):
        return False
    
    # Check minimum length (OpenAI keys are typically long)
    if len(api_key) < 20:
        return False
    
    return True
