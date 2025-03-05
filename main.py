import asyncio
import logging
import time
from telethon import TelegramClient, events, Button
from datetime import datetime

# Enable logging
logging.basicConfig(filename="message_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Telegram API credentials
api_id = 20094764  
api_hash = "ac33c77cfdbe4f94ebd73dde27b4a10c"
number = "+8801790168428"  
username = "@darkkkjht"  

# Start the client
client = TelegramClient("auto_reply_session", api_id, api_hash)

# Dictionary to track last reply time
user_last_reply = {}

# Time in seconds to prevent duplicate replies (e.g., 60 seconds)
REPLY_COOLDOWN = 60  

# Custom replies based on keywords
KEYWORD_RESPONSES = {
    "hello": "Hello! How can I assist you today?",
    "assalamu alaikum": "Wa Alaikum Assalam! How can I help you?",
    "price": "Please visit our website for pricing details: https://example.com",
    "contact": "You can contact our admin directly using the button below.",
    "help": "Here are some commands you can use:\n- 'Price' for pricing info\n- 'Contact' for admin support\n- 'Website' for more details."
}

# Default response for any message
DEFAULT_REPLY = "Thank you for your message! We will get back to you soon. Type 'help' for more options."

# Buttons for quick actions
BUTTONS = [
    [Button.text("📞 Contact Admin", resize=True), Button.url("🌐 Visit Website", "https://example.com")]
]

# Auto-reply to private and group messages
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    sender = await event.get_sender()
    sender_id = sender.id
    sender_name = sender.first_name if sender else "Unknown"
    sender_username = sender.username if sender.username else ""
    sender_phone = sender.phone if sender.phone else ""

    # Determine chat type
    chat_type = "Private Chat" if event.is_private else f"Group Chat ({event.chat.title})"

    message_text = event.text.lower().strip()  # Convert to lowercase for case-insensitive matching
    current_time = time.time()

    # Check if the user was replied to recently (cooldown system)
    if sender_id in user_last_reply and (current_time - user_last_reply[sender_id]) < REPLY_COOLDOWN:
        print(f"Skipping reply to {sender_name}, cooldown active.")
        return  

    # Update last reply time
    user_last_reply[sender_id] = current_time

    # Log message details
    log_entry = f"{datetime.now()} - {chat_type} - {sender_name} (@{sender_username}): {message_text}"
    logging.info(log_entry)
    print(log_entry)

    # Determine response based on keywords or send a default reply
    reply_message = DEFAULT_REPLY  # Default response
    for keyword, response in KEYWORD_RESPONSES.items():
        if keyword in message_text:
            reply_message = response
            break  # Stop checking after the first match

    # Send the reply with buttons
    try:
        await event.reply(reply_message, buttons=BUTTONS)
        print(f"Replied to {sender_name} with: {reply_message}")
    except Exception as e:
        logging.error(f"Error replying to {sender_name}: {e}")

# Start the bot
print("Advanced Auto-Reply Bot is running...")
client.start()
client.run_until_disconnected()
