"""
Main module for the OpenAI poem generator application.

This console application retrieves the current date and uses OpenAI's API
to generate a poem about that date.
"""

import datetime
import os
import sys
from openai import OpenAI

def get_current_date():
    """
    Get the current date formatted as a string.
    
    Returns:
        str: Current date in the format 'Month Day, Year' (e.g., 'May 23, 2025')
    """
    today = datetime.datetime.now()
    return today.strftime("%B %d, %Y")

def generate_poem(date_str):
    """
    Generate a poem about the given date using OpenAI's API.
    
    Args:
        date_str (str): The date to generate a poem about
        
    Returns:
        str: The generated poem
    """
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return f"Error: OPENAI_API_KEY environment variable not set. Please set it before running the application."
    
    client = OpenAI(api_key=api_key)
    
    # Create the prompt for the OpenAI model
    prompt = f"Write a creative and thoughtful poem about the date {date_str}. " \
             f"The poem should reflect on the significance of this day, the season, " \
             f"and perhaps historical events or cultural associations with this time of year."
    
    try:
        # Call the OpenAI API to generate the poem
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled poet who creates beautiful, meaningful poems about dates."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return the poem from the response
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating poem: {e}")
        return f"Could not generate a poem for {date_str}. Error: {str(e)}"

def main():
    """
    Main function that runs the application.
    
    Gets the current date, generates a poem about it using OpenAI's API,
    and prints the result to the console.
    """
    print("OpenAI Poem Generator")
    print("=====================")
    
    # Get the current date
    current_date = get_current_date()
    print(f"\nToday's date: {current_date}")
    
    print("\nGenerating poem...")
    
    # Generate a poem about the current date
    poem = generate_poem(current_date)
    
    # Print the generated poem
    print("\nYour poem about today:\n")
    print(poem)
    print("\n=====================")

if __name__ == "__main__":
    main()
