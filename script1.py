import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext
from PIL import Image
from io import BytesIO
import nest_asyncio
import re
import os

# Apply nest_asyncio to enable asyncio in nested environments like Jupyter or multi-threaded apps
nest_asyncio.apply()

# URL for the logo image
LOGO_URL = "https://file-to-link-nx-ccf8d5eda5c0.herokuapp.com/dl/678e7aea06473a030935a6d8"

# Path to save the logo
LOGO_PATH = "downloaded_logo.png"

# Download the logo image from the URL using aiohttp for async behavior
async def download_logo(url: str, save_path: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())
                    print(f"Logo saved to {save_path}")
                else:
                    print(f"Failed to download logo. Status code: {response.status}")
        except Exception as e:
            print(f"Error downloading logo: {e}")

# Ensure the logo is downloaded once at the start
async def ensure_logo_downloaded():
    if not os.path.exists(LOGO_PATH):
        await download_logo(LOGO_URL, LOGO_PATH)

# Define the customized caption with title support
def get_custom_caption(link, title):
    return f"""
🎃 ᴘᴏᴡᴇʀᴇᴅ ʙʏ↓ Telegram                
                🍯 @HotError      

Title - {title}
⌬ Hot Error
╰─➩ {link}

Other Categories ↓ 🥵⚡
https://t.me/HotError
"""

# Function to add logo to image
def add_logo_to_image(photo: Image.Image, logo_path: str) -> Image.Image:
    # Open the logo image
    logo = Image.open(logo_path)

    # Resize logo if necessary (optional, adjust as needed)
    logo_width = photo.width // 3  # Resize logo to 1/3rd of the image width
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    # Position the logo at the top center of the photo
    position = ((photo.width - logo.width) // 2, 0)

    # Paste the logo on the photo
    photo.paste(logo, position, logo.convert("RGBA"))
    return photo

# Function to handle received media and customize the caption
async def handle_media(update: Update, context: CallbackContext):
    media = None
    caption = None
    link = ""
    title = "No Title"  # Default title if no Title= pattern is found

    # Only handle media messages that have a caption (e.g., photo, video, etc.)
    if update.message.photo:
        caption = update.message.caption
        media = update.message.photo[-1]  # Take the highest quality photo
    elif update.message.video:
        caption = update.message.caption
        media = update.message.video
    elif update.message.document:
        caption = update.message.caption
        media = update.message.document
    elif update.message.voice:
        caption = update.message.caption
        media = update.message.voice
    elif update.message.animation:
        caption = update.message.caption
        media = update.message.animation

    # If a caption exists, check if it contains the Title= pattern
    if caption:
        title_match = re.search(r"Title=\s?\{(.*?)\}", caption)  # Regex to extract title inside {}

        if title_match:
            title = title_match.group(1).strip()  # Extracted title inside the {}

        # Use a regex to extract only the link (http or https)
        link_match = re.search(r"https?://[^\s]+", caption)
        if link_match:
            link = link_match.group(0)  # Extract the full link

        custom_caption = get_custom_caption(link, title)  # Use extracted title

        # If the media is a photo, download, process and send with the custom caption
        if update.message.photo:
            # Download the image
            photo_file = await media.get_file()
            photo_bytes = await photo_file.download_as_bytearray()

            # Open the image with Pillow
            photo = Image.open(BytesIO(photo_bytes))

            # Resize the image if needed (optional)
            max_width = 1080  # Max width you want for the image
            if photo.width > max_width:
                ratio = max_width / float(photo.width)
                new_height = int((float(photo.height) * float(ratio)))
                photo = photo.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Add the logo to the photo
            photo_with_logo = add_logo_to_image(photo, LOGO_PATH)

            # Save the modified image to a BytesIO object
            output = BytesIO()
            photo_with_logo.save(output, format="PNG")
            output.seek(0)

            # Send the modified image with the custom caption
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output, caption=custom_caption)

        # For video, document, voice note, and animation, just send the media with the custom caption
        elif update.message.video:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=media.file_id, caption=custom_caption)
        elif update.message.document:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=media.file_id, caption=custom_caption)
        elif update.message.voice:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=media.file_id, caption=custom_caption)
        elif update.message.animation:
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation=media.file_id, caption=custom_caption)

# Function to start the bot and process incoming updates
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot is running and ready to process media sent by anyone.")

# 
