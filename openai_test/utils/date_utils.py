"""
Date utility functions for the OpenAI poem generator.
"""

import datetime

def get_current_date():
    """
    Get the current date formatted as a string.
    
    Returns:
        str: Current date in the format 'Month Day, Year' (e.g., 'May 23, 2025')
    """
    today = datetime.datetime.now()
    return today.strftime("%B %d, %Y")
