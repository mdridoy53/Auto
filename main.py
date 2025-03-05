import random
import string
from pyrogram import Client, filters

# Telegram Bot Token (Get from @BotFather)
BOT_TOKEN = "7805081492:AAGktpvpVfMvx98xJKEfQz2OFnyTmcz4uAw"

# Create a Pyrogram Client
app = Client("combo_bot", bot_token=BOT_TOKEN)

def generate_combo():
    """Generates a random Outlook email and password combination."""
    domains = ["outlook.com", "hotmail.com", "live.com"]
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@{random.choice(domains)}"
    
    password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    
    gmail_email = f"{username}@gmail.com"
    gmail_password = password[:8]  # Save first 8 digits for Gmail
    
    return email, password, gmail_email, gmail_password

def generate_url():
    """Generates a random PHP admin URL."""
    base_url = "http://example.com/admin/"
    random_path = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    full_url = f"{base_url}{random_path}.php"

    return full_url

@app.on_message(filters.command("combo"))
async def send_combo(client, message):
    """Handles the /combo command."""
    email, password, gmail_email, gmail_password = generate_combo()

    combo_text = f"{email}:{password}\n{gmail_email}:{gmail_password}\n"

    # Save to combo.txt
    with open("combo.txt", "a") as file:
        file.write(combo_text)

    # Send the response
    await message.reply_text(f"Generated Combo:\n{combo_text}")

@app.on_message(filters.command("url"))
async def send_url(client, message):
    """Handles the /url command."""
    url = generate_url()

    # Save to url.txt
    with open("url.txt", "a") as file:
        file.write(url + "\n")

    # Send the response
    await message.reply_text(f"Generated Admin URL:\n{url}")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
