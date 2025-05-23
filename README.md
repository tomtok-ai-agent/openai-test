# OpenAI Test

A console application that uses OpenAI API to generate a poem about the current date.

## Description

This Python application retrieves the current date and uses OpenAI's API to generate a creative poem about that date. The poem reflects on the significance of the day, the season, and potentially historical events or cultural associations with that time of year.

## Features

- Gets the current date automatically
- Uses OpenAI's API to generate a unique poem
- Handles API errors gracefully with detailed feedback
- Secure API key management using environment variables
- Response caching to reduce API calls and costs
- API usage tracking for monitoring token consumption
- Comprehensive logging system
- Extensive CLI options for customization
- Modular architecture for easy extension
- Test suite with mocking support

## Requirements

- Python 3.11 or higher
- Poetry for dependency management
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tomtok-ai-agent/openai-test.git
cd openai-test
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage

Run the application using Poetry:
```bash
poetry run python -m openai_test.main
```

The application will display the current date and generate a poem about it.

### Advanced CLI Options

The application supports various command-line options:

```bash
poetry run python -m openai_test.main --help
```

Available options:

| Option | Description |
|--------|-------------|
| `--date DATE` | Date to generate poem about (default: today). Format: 'Month Day, Year' |
| `--model MODEL` | OpenAI model to use (default: gpt-3.5-turbo) |
| `--temperature TEMP` | Temperature parameter for generation (default: 0.7) |
| `--max-tokens TOKENS` | Maximum tokens to generate (default: 500) |
| `--log-level LEVEL` | Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO) |
| `--no-cache` | Disable response caching |
| `--clear-cache` | Clear response cache before generating |
| `--show-usage` | Show API usage summary after generation |

### Examples

Generate a poem about a specific date:
```bash
poetry run python -m openai_test.main --date "December 25, 2025"
```

Use a different model with higher creativity:
```bash
poetry run python -m openai_test.main --model "gpt-4" --temperature 0.9
```

Generate a shorter poem:
```bash
poetry run python -m openai_test.main --max-tokens 200
```

View API usage statistics:
```bash
poetry run python -m openai_test.main --show-usage
```

Force a fresh response by bypassing cache:
```bash
poetry run python -m openai_test.main --no-cache
```

## Caching System

The application includes a response caching system to reduce API calls and costs. When you request a poem with the same parameters (date, model, temperature, etc.), the application will use the cached response if available.

### Cache Configuration

By default, cache entries expire after 24 hours. The cache is stored in `~/.openai_poem/cache/`.

### Cache Management

You can manage the cache using these CLI options:

- `--no-cache`: Bypass the cache and force a new API call
- `--clear-cache`: Clear expired cache entries before generating a new poem

## API Usage Tracking

The application tracks API usage to help monitor costs and usage patterns. Usage data is stored in `~/.openai_poem/usage.json`.

### Viewing Usage Statistics

Use the `--show-usage` option to display usage statistics after generating a poem:

```bash
poetry run python -m openai_test.main --show-usage
```

This will show:
- Total number of API requests
- Total tokens consumed
- Today's usage breakdown
- Per-model statistics

## Logging

The application uses a comprehensive logging system that logs to both console and file:

- Console: Shows high-level information by default
- File: Logs detailed information to `openai_poem.log`

You can adjust the logging level using the `--log-level` option:

```bash
poetry run python -m openai_test.main --log-level DEBUG
```

## Security

### API Key Management

This application uses environment variables for API key management to ensure security. Never hardcode your API key in the source code or commit it to version control.

#### Development Environment

For local development, we recommend using a `.env` file:

```bash
# .env
OPENAI_API_KEY=your-api-key-here
```

Make sure to add `.env` to your `.gitignore` file and use the `python-dotenv` package to load the variables:

```python
from dotenv import load_dotenv
load_dotenv()  # loads variables from .env
```

#### Testing Environment

For CI/CD pipelines, use the secrets management provided by your platform:

- **GitHub Actions**: Use repository secrets
- **GitLab CI**: Use CI/CD variables
- **Jenkins**: Use the Credentials Plugin

#### Production Environment

In production, use a secure secrets management system:

- **Kubernetes**: Use Kubernetes Secrets
- **AWS**: Use AWS Secrets Manager
- **Azure**: Use Azure Key Vault
- **Docker**: Use Docker secrets or environment variables

### API Key Validation

The application validates the format of your API key before making requests to ensure early detection of configuration issues. Valid OpenAI API keys typically:

- Start with the prefix `sk-`
- Have sufficient length (at least 20 characters)
- Contain only valid characters

If your API key is rejected, please verify that you're using a valid OpenAI API key and that it's correctly set in your environment.

## Testing

The project includes a comprehensive test suite:

```bash
poetry run pytest
```

The tests use mocking to avoid actual API calls, making them suitable for CI/CD pipelines.

### Test Structure

The test suite is organized in the `tests` directory with the following structure:

- `test_openai_client.py`: Tests for the OpenAI API client wrapper
- `test_main.py`: Tests for the main application functionality

### Running Specific Tests

You can run specific test files or test cases:

```bash
# Run a specific test file
poetry run pytest tests/test_openai_client.py

# Run tests with verbose output
poetry run pytest -v

# Run tests with specific markers
poetry run pytest -m "not slow"
```

### Test Coverage

The tests cover key functionality including:
- OpenAI client text generation
- Response caching
- Error handling
- Command-line interface
- API usage tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
