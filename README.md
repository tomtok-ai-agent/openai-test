# OpenAI Test

A console application that uses OpenAI API to generate a poem about the current date.

## Description

This Python application retrieves the current date and uses OpenAI's API to generate a creative poem about that date. The poem reflects on the significance of the day, the season, and potentially historical events or cultural associations with that time of year.

## Features

- Gets the current date automatically
- Uses OpenAI's API to generate a unique poem
- Handles API errors gracefully
- Secure API key management using environment variables

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

Run the application using Poetry:
```bash
poetry run python -m openai_test.main
```

The application will display the current date and generate a poem about it.

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
