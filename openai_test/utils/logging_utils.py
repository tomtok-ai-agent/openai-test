"""
Logging configuration and utilities for the OpenAI poem generator.
"""

import logging
import sys

def setup_logging(log_file="openai_poem.log", console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configure application logging with both file and console handlers.
    
    Args:
        log_file (str): Path to the log file
        console_level (int): Logging level for console output
        file_level (int): Logging level for file output
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("openai_poem")
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    
    # Create formatters
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set formatters
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
