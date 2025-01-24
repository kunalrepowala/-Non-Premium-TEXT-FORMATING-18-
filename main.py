import logging
import asyncio
import os  # Import os module to fetch environment variables
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from web_server import start_web_server  # Import the web server function
from script1 import download_and_resize_logo, get_custom_caption, add_logo_to_image, handle_media, start  # Import relevant functions

# Set up logging to monitor bot and server activities
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to start the Telegram bot
async def run_bot() -> None:
    # Get the bot token from environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Fetch the bot token from the environment

    if not bot_token:
        raise ValueError("No TELEGRAM_BOT_TOKEN environment variable found")  # Ensure the token is available
    
    app = ApplicationBuilder().token(bot_token).build()  # Initialize the bot application using the token

        app.add_handler(CommandHandler("start", start))  # Command handler for '/start'

    # Add message handlers for different types of media
    app.add_handler(MessageHandler(filters.PHOTO, handle_media))   # Handle photo messages
    app.add_handler(MessageHandler(filters.VIDEO, handle_media))   # Handle video messages
    app.add_handler(MessageHandler(filters.DOCUMENT, handle_media))  # Handle document messages
    app.add_handler(MessageHandler(filters.VOICE, handle_media))  # Handle voice messages
    app.add_handler(MessageHandler(filters.ANIMATION, handle_media))  # Handle animation messages
    app.add_handler(MessageHandler(filters.ALL, handle_media))  # Handle all other messages

    # Log when the bot is starting
    logger.info("Starting the Telegram bot...")
    
    # Start the bot with polling
    await app.run_polling()

# Main entry point to start both bot and web server concurrently
async def main() -> None:
    try:
        # Run both the bot and the web server concurrently using asyncio
        await asyncio.gather(run_bot(), start_web_server())
    except Exception as e:
        logger.error(f"Error occurred: {e}")  # Log any errors that occur

# Start the program
if __name__ == '__main__':
    try:
        # Run the asyncio event loop for both the bot and the web server
        logger.info("Starting the bot and web server concurrently...")
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error starting the bot and web server: {e}")
