@echo off
REM Script to run the Telegram bot on Windows

REM Check if .env file exists
IF NOT EXIST .env (
    echo Environment file (.env) not found!
    echo Please create a .env file with your bot token.
    echo Use .env.example as a template.
    pause
    exit /b 1
)

REM Load environment variables
FOR /f "tokens=*" %%i IN ('type .env') DO SET %%i

REM Check if required environment variables are set
IF "%TELEGRAM_BOT_TOKEN%"=="" (
    echo TELEGRAM_BOT_TOKEN environment variable is not set!
    echo Please add your bot token to the .env file.
    pause
    exit /b 1
)

echo Starting Telegram bot...
python bot.py

pause