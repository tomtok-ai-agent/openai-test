"""
Configuration settings for the OpenAI poem generator.
"""

# OpenAI API settings
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.7

# Prompt settings
SYSTEM_PROMPT = "You are a skilled poet who creates beautiful, meaningful poems about dates."
USER_PROMPT_TEMPLATE = "Write a creative and thoughtful poem about the date {date}. " \
                      "The poem should reflect on the significance of this day, the season, " \
                      "and perhaps historical events or cultural associations with this time of year."
