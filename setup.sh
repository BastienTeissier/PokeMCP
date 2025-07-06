#!/bin/bash

# Setup script for Pokemon MCP authentication

echo "Setting up Pokemon MCP with OAuth2 authentication..."

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your Google OAuth credentials"
fi

# Create keys directory
mkdir -p keys

# Install dependencies
echo "Installing dependencies..."
if command -v poetry &>/dev/null; then
    poetry install
else
    pip install -e .
fi

# Initialize database with Alembic
echo "Setting up database migrations..."
if [ ! -d "alembic" ]; then
    poetry run alembic init alembic
fi

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your Google OAuth2 credentials"
echo "2. Run 'docker-compose up --build' to start all services"
echo "3. Visit http://localhost:8000/login to test authentication"
