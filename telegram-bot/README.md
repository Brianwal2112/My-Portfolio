# Telegram Profile Sharing Bot

A Telegram bot that shares your X (formerly Twitter) and GitHub profile links when you're not around.

## Features

- Share your X profile link
- Share your GitHub profile link
- Share both profiles at once
- Interactive buttons for easy navigation
- Multiple commands for different use cases

## Commands

- `/start` - Start the bot and see the main menu
- `/help` - Show help message
- `/profiles` - Get both profile links
- `/x` - Get X profile link
- `/github` - Get GitHub profile link

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and use the `/newbot` command
3. Follow the prompts to create your bot and get the API token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project directory with the following content:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with the token you received from BotFather.

### 4. Update Profile Links

Open `bot.py` and update the following variables with your actual profile links:

```python
X_PROFILE_LINK = "https://x.com/your_username"  # Replace with your X profile
GITHUB_PROFILE_LINK = "https://github.com/your_username"  # Replace with your GitHub profile
```

### 5. Run the Bot

```bash
python bot.py
```

## Configuration

To customize the bot for your profiles:

1. Replace the placeholder URLs in the code with your actual profile links
2. Customize the messages and responses as needed
3. Add any additional features you'd like

## Deployment Options

### Local Development
Run the bot on your local machine by following the setup instructions above.

### Heroku Deployment
1. Create a `Procfile` with the content: `worker: python bot.py`
2. Deploy to Heroku with the TELEGRAM_BOT_TOKEN environment variable set

### Docker Deployment
1. Create a Dockerfile
2. Build and run the container with the environment variable set

## Security Notes

- Never commit your bot token to version control
- Use environment variables to store sensitive information
- Keep your bot token secure and private

## Troubleshooting

If the bot isn't responding:
1. Check that the bot token is correct
2. Verify that the environment variable is set
3. Ensure your profile links are valid URLs
4. Check the logs for any error messages

## Contributing

Feel free to fork this repository and submit pull requests for improvements.