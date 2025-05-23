"""
Main module for the OpenAI poem generator application.

This console application retrieves the current date and uses OpenAI's API
to generate a poem about that date.
"""

import os
import logging
import argparse
from .config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .api.client_factory import ClientFactory
from .utils.date_utils import get_current_date
from .utils.security import validate_api_key

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("openai_poem.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("openai_poem")

def generate_poem(date_str):
    """
    Generate a poem about the given date using OpenAI's API.
    
    Args:
        date_str (str): The date to generate a poem about
        
    Returns:
        str: The generated poem or error message
        
    Raises:
        ValueError: If the API key is not set or invalid
        ConnectionError: If the connection to the API fails
    """
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set. Please set it before running the application."
    
    # Validate API key format
    if not validate_api_key(api_key):
        return "Error: OPENAI_API_KEY has invalid format. Please check your API key."
    
    try:
        # Create OpenAI client
        client = ClientFactory.create_openai_client(api_key=api_key)
        
        # Format the user prompt with the date
        user_prompt = USER_PROMPT_TEMPLATE.format(date=date_str)
        
        # Generate the poem
        return client.generate_text(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
    
    except Exception as e:
        logger.error(f"Error generating poem: {str(e)}")
        return f"Could not generate a poem for {date_str}. Error: {str(e)}"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate a poem about a date using OpenAI API")
    
    parser.add_argument("--date", type=str, 
                        help="Date to generate poem about (default: today). Format: 'Month Day, Year'")
    
    return parser.parse_args()

def main():
    """
    Main function that runs the application.
    
    Gets the current date, generates a poem about it using OpenAI's API,
    and prints the result to the console.
    """
    # Parse arguments
    args = parse_arguments()
    
    print("OpenAI Poem Generator")
    print("=====================")
    
    # Get the date
    if args.date:
        current_date = args.date
    else:
        current_date = get_current_date()
    
    print(f"\nDate: {current_date}")
    print("\nGenerating poem...")
    
    # Generate a poem about the current date
    poem = generate_poem(current_date)
    
    # Print the generated poem
    print("\nYour poem about this date:\n")
    print(poem)
    print("\n=====================")

if __name__ == "__main__":
    main()
