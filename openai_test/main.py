"""
Main module for the OpenAI poem generator application.

This console application retrieves the current date and uses OpenAI's API
to generate a poem about that date.
"""

import os
import argparse
import logging
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError, BadRequestError

from .config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .api.client_factory import ClientFactory
from .utils.date_utils import get_current_date
from .utils.security import validate_api_key
from .utils.logging_utils import setup_logging

# Setup logging
logger = setup_logging()

def generate_poem(date_str, model=None, temperature=None, max_tokens=None, use_cache=True):
    """
    Generate a poem about the given date using OpenAI's API.
    
    Args:
        date_str (str): The date to generate a poem about
        model (str, optional): OpenAI model to use
        temperature (float, optional): Temperature parameter for generation
        max_tokens (int, optional): Maximum tokens to generate
        use_cache (bool, optional): Whether to use response caching
        
    Returns:
        str: The generated poem or error message
        
    Raises:
        ValueError: If the API key is not set or invalid
        ConnectionError: If the connection to the API fails
    """
    logger.info(f"Generating poem about date: {date_str}")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return "Error: OPENAI_API_KEY environment variable not set. Please set it before running the application."
    
    # Validate API key format
    if not validate_api_key(api_key):
        logger.error("OPENAI_API_KEY has invalid format")
        return "Error: OPENAI_API_KEY has invalid format. Please check your API key."
    
    try:
        # Create OpenAI client
        client = ClientFactory.create_openai_client(api_key=api_key, use_cache=use_cache)
        
        # Format the user prompt with the date
        user_prompt = USER_PROMPT_TEMPLATE.format(date=date_str)
        
        # Generate the poem
        poem = client.generate_text(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info("Poem generated successfully")
        return poem
    
    except AuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        return f"Error: Authentication failed. Please check your API key. Details: {str(e)}"
        
    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {str(e)}")
        return f"Error: Rate limit exceeded. Please try again later. Details: {str(e)}"
        
    except APIConnectionError as e:
        logger.error(f"API connection error: {str(e)}")
        return f"Error: Could not connect to OpenAI API. Please check your internet connection. Details: {str(e)}"
        
    except BadRequestError as e:
        logger.error(f"Bad request error: {str(e)}")
        return f"Error: Invalid request parameters. Details: {str(e)}"
        
    except APIError as e:
        logger.error(f"API error: {str(e)}")
        return f"Error: OpenAI API returned an error. Details: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error generating poem: {str(e)}")
        return f"Error: An unexpected error occurred while generating a poem for {date_str}. Details: {str(e)}"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate a poem about a date using OpenAI API")
    
    parser.add_argument("--date", type=str, 
                        help="Date to generate poem about (default: today). Format: 'Month Day, Year'")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo",
                        help="OpenAI model to use (default: gpt-3.5-turbo)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature parameter for generation (default: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=500,
                        help="Maximum tokens to generate (default: 500)")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO",
                        help="Logging level (default: INFO)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Disable response caching")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Clear response cache before generating")
    parser.add_argument("--show-usage", action="store_true",
                        help="Show API usage summary after generation")
    
    return parser.parse_args()

def main():
    """
    Main function that runs the application.
    
    Gets the current date, generates a poem about it using OpenAI's API,
    and prints the result to the console.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Set logging level
    if args.log_level:
        numeric_level = getattr(logging, args.log_level.upper(), None)
        if numeric_level:
            logger.setLevel(numeric_level)
    
    print("OpenAI Poem Generator")
    print("=====================")
    
    # Get the date
    if args.date:
        current_date = args.date
    else:
        current_date = get_current_date()
    
    print(f"\nDate: {current_date}")
    
    # Clear cache if requested
    if args.clear_cache:
        try:
            client = ClientFactory.create_openai_client()
            cleared = client.clear_cache()
            print(f"\nCleared {cleared} cached responses")
        except Exception as e:
            print(f"\nError clearing cache: {str(e)}")
    
    print("\nGenerating poem...")
    
    # Generate a poem about the current date
    poem = generate_poem(
        date_str=current_date,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        use_cache=not args.no_cache
    )
    
    # Print the generated poem
    print("\nYour poem about this date:\n")
    print(poem)
    print("\n=====================")
    
    # Show usage summary if requested
    if args.show_usage:
        try:
            client = ClientFactory.create_openai_client()
            usage = client.get_usage_summary()
            
            if usage:
                print("\nAPI Usage Summary:")
                print(f"Total requests: {usage['total_requests']}")
                print(f"Total tokens: {usage['total_tokens']}")
                
                # Show today's usage if available
                import datetime
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                if today in usage["requests_by_date"]:
                    today_usage = usage["requests_by_date"][today]
                    print(f"\nToday's usage:")
                    print(f"  Requests: {today_usage['requests']}")
                    print(f"  Tokens: {today_usage['tokens']}")
                    print(f"  Successful: {today_usage['successful_requests']}")
                    print(f"  Failed: {today_usage['failed_requests']}")
            else:
                print("\nNo usage data available")
        except Exception as e:
            print(f"\nError retrieving usage data: {str(e)}")

if __name__ == "__main__":
    main()
