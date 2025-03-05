import telebot
import random
import datetime
import requests
import os
import re  

# ✅ Securely Load Telegram Bot Token
TOKEN = "7868412572:AAFmnuqTxofdZL0Em63QdRF1qM9Q794rKAY"  # Replace with a secure token from BotFather

bot = telebot.TeleBot(TOKEN)

# ✅ Set Your Channel (Users Must Join to Use the Bot)
CHANNEL_USERNAME = "dar3658"  # Replace with your channel username (without @)
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# ✅ Function to Check if a User is in the Channel
def is_user_in_channel(user_id):
    try:
        response = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return response.status in ["member", "administrator", "creator"]
    except:
        return False  # If error, assume the user is not a member

# ✅ Function to Fetch BIN Details
def bin_lookup(bin_number):
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=5)
        response.raise_for_status()
        data = response.json()
        return (
            data.get('scheme', 'Unknown').capitalize(),
            data.get('bank', {}).get('name', 'Unknown'),
            data.get('country', {}).get('name', 'Unknown')
        )
    except requests.exceptions.RequestException:
        return 'Unknown', 'Unknown', 'Unknown'

# ✅ Function to Validate Card Number (Luhn Algorithm)
def luhn_algorithm(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

# ✅ Function to Generate a Valid Card
def generate_card(bin_number):
    if len(bin_number) not in [6, 8, 9]:
        return None, None, None

    card_body = bin_number + "".join(str(random.randint(0, 9)) for _ in range(16 - len(bin_number) - 1))
    for last_digit in range(10):
        potential_card = card_body + str(last_digit)
        if luhn_algorithm(potential_card):
            card_type, issuer, country = bin_lookup(bin_number)
            expiry_month = str(random.randint(1, 12)).zfill(2)
            expiry_year = str(random.randint(datetime.datetime.now().year % 100, 29))
            cvc = str(random.randint(100, 999))
            return f"{potential_card}|{expiry_month}|{expiry_year}|{cvc}", card_type, issuer, country
    return None, None, None

# ✅ Function to Generate Fake Email Combos
def generate_fake_combo(quantity):
    domains = ["gmail.com", "outlook.com"]
    combos = []

    for _ in range(quantity):
        username = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=12))
        domain = random.choice(domains)
        email = f"{username}@{domain}"
        password = username[:8]  # First 8 characters of the email as the password
        combos.append(f"{email}|{password}")

    return combos

# ✅ Function to Extract Card Data from Messages
def extract_cards(text):
    card_pattern = re.compile(r"\b(\d{16})\|(\d{2})\|(\d{2})\|(\d{3})\b")
    return [match.group() for match in card_pattern.finditer(text)]

# ✅ Command: /start (Join Requirement)
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id

    if is_user_in_channel(user_id):
        bot.send_message(
            message.chat.id,
            f"✅ **Welcome to Advanced Generator & Checker Bot!**\n"
            f"🔹 You now have full access to the bot.\n\n"
            f"🛠 **Commands:**\n"
            f"📌 `/gen 6xxxxx 5` → Generate credit cards\n"
            f"📌 `/chk 4147201234567890` → Check card validity\n"
            f"📌 `/combo 10` → Generate email combos\n"
            f"📌 `/scr @groupusername` → Scrape and clean card details\n"
            f"📌 `/txt any_text_here` → Clean text\n"
            f"📌 **Send a file** to clean and get `Clear.txt`\n\n"
            f"💬 Join our channel for updates: [Join Here]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
    else:
        join_button = telebot.types.InlineKeyboardMarkup()
        join_button.add(telebot.types.InlineKeyboardButton("🔗 Join Channel", url=CHANNEL_LINK))
        
        bot.send_message(
            message.chat.id,
            "⚠️ **You must join our channel to use this bot!**\n"
            "📢 Click the button below to join, then restart the bot.",
            reply_markup=join_button
        )

# ✅ Command: /combo (Generate & Send Fake Email Combos)
@bot.message_handler(commands=['combo'])
def generate_combo_file(message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.reply_to(message, "⚠️ **Invalid format!** Use: `/combo 10`")
        return

    quantity = int(args[1])
    if quantity > 50:
        bot.reply_to(message, "⚠️ **Max limit is 50 combos per request!**")
        return

    combos = generate_fake_combo(quantity)
    file_path = "Combo.txt"
    with open(file_path, "w") as file:
        file.write("\n".join(combos))

    with open(file_path, "rb") as file:
        bot.send_document(message.chat.id, file, caption=f"✅ **Generated {quantity} combos successfully!**\n📂 **File:** Combo.txt")

# ✅ Command: /scr (Scrape & Clean Card Data from a Public Group)
@bot.message_handler(commands=['scr'])
def scrape_group_cards(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Please specify a public group!** Use: `/scr @groupusername`")
        return

    group_username = args[1]
    messages = bot.get_chat_history(group_username, limit=100)  # Fetch last 100 messages
    raw_cards = set()

    for msg in messages.messages:
        if msg.text:
            extracted_cards = extract_cards(msg.text)
            raw_cards.update(extracted_cards)

    if not raw_cards:
        bot.reply_to(message, "❌ **No valid card details found in the group!**")
        return

    file_path = "Card.txt"
    with open(file_path, "w") as file:
        file.write("\n".join(raw_cards))

    with open(file_path, "rb") as file:
        bot.send_document(message.chat.id, file, caption=f"✅ **Extracted {len(raw_cards)} valid cards!**\n📂 **File:** Card.txt")

# ✅ Start bot polling
bot.polling()
