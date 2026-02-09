#!/bin/bash
# Script to run the Telegram bot

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Environment file (.env) not found!"
    echo "Please create a .env file with your bot token."
    echo "Use .env.example as a template."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check if required environment variables are set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "TELEGRAM_BOT_TOKEN environment variable is not set!"
    echo "Please add your bot token to the .env file."
    exit 1
fi

echo "Starting Telegram bot..."
python bot.py