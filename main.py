import telebot
import random
import datetime
import requests
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7805081492:AAHiW1kaxnCupaqR1zPYwKwFb8raqNTBQiE"
CHANNEL_USERNAME = "dar3658"
CHANNEL_LINK = "https://t.me/dar3658"
ADMIN_ID = 7987662357  
APPROVAL_RATE = 70  
CHK_COST = 2  
CHKK_COST = 5  
CHKKK_COST = 0.50  
JOIN_BONUS = 20  
REFER_BONUS = 20  

bot = telebot.TeleBot(TOKEN)
users = {}  
redeem_codes = {}  

# ✅ Check if user is a member of the channel
def is_user_member(user_id):
    try:
        member_status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status
        return member_status in ["member", "administrator", "creator"]
    except:
        return False

# ✅ Force users to join the channel
def force_join_message(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Join Channel", url=CHANNEL_LINK))
    bot.send_message(chat_id, "⚠️ **You must join our official channel to use this bot!**", reply_markup=markup)

# ✅ Register a new user with starting credits
def add_user(user_id):
    if user_id not in users:
        users[user_id] = {"credits": JOIN_BONUS, "is_premium": False, "banned": False, "referrals": 0}

# ✅ **ADMIN: Add Premium User**
@bot.message_handler(commands=['addpremium'])
def add_premium(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ **You don't have permission to use this command!**")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Use:** `/addpremium USER_ID`")
        return

    target_user_id = int(args[1])
    add_user(target_user_id)
    users[target_user_id]['is_premium'] = True
    bot.reply_to(message, f"✅ **User {target_user_id} is now a premium user!**")

# ✅ **START Command**
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    if not is_user_member(user_id):
        force_join_message(user_id)
        return

    add_user(user_id)
    bot.send_message(
        user_id,
        f"🎉 **Welcome to Card Checker Bot v8.2!** 🎉\n"
        f"You have **{users[user_id]['credits']} credits**.\n"
        f"Refer users and earn **{REFER_BONUS} credits** per referral!\n\n"
        f"🛠 **Commands:**\n"
        f"📌 `/chk xxxxxxxxxxxxxxxx|xx|xxxx|xxx` → Costs **2 credits** per check.\n"
        f"📌 `/chkk card1|mm|yy|cvv card2|mm|yy|cvv ...` → **Premium Only** (Costs 5 credits).\n"
        f"📌 `/chkkk` → **Upload a TXT file** (Premium Only, $0.50 per approved card).\n"
        f"📌 `/redeem CODE` → Redeem free credits.\n"
        f"📌 `/credits` → Check your balance.\n\n"
        f"💬 Join our channel: [Click Here]({CHANNEL_LINK})",
        parse_mode="Markdown"
    )

# ✅ **Check User Credits**
@bot.message_handler(commands=['credits'])
def check_credits(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 **You have {users[user_id]['credits']} credits.**")

# ✅ **Redeem Code**
@bot.message_handler(commands=['redeem'])
def redeem_code(message):
    user_id = message.chat.id
    args = message.text.split()
    if len(args) < 2 or args[1] not in redeem_codes:
        bot.reply_to(message, "⚠️ **Invalid or expired redeem code!**")
        return

    credits = redeem_codes.pop(args[1])
    users[user_id]['credits'] += credits
    bot.reply_to(message, f"🎉 **Redeemed {credits} credits!** You now have {users[user_id]['credits']} credits.")

# ✅ **ADMIN: Generate Redeem Code**
@bot.message_handler(commands=['make_redeem'])
def make_redeem_code(message):
    if message.chat.id != ADMIN_ID:
        return

    code = f"RC{random.randint(10000, 99999)}"
    redeem_codes[code] = 10  
    bot.reply_to(message, f"🎁 **Redeem Code Created:** `{code}` (10 credits)")

# ✅ **ADMIN: Ban User**
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.chat.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Use:** `/ban USER_ID`")
        return

    user_id = int(args[1])
    users[user_id]['banned'] = True
    bot.reply_to(message, f"✅ **User {user_id} has been banned.**")

# ✅ **Handle TXT file upload for bulk checking**
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    user_id = message.chat.id
    if not is_user_member(user_id):
        force_join_message(user_id)
        return

    if not users[user_id]["is_premium"]:
        bot.reply_to(message, "⚠️ **This feature is only available for premium users!**")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(f"{user_id}.txt", 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "🔍 **File received. Checking cards...** Please wait.")
    time.sleep(3)

    approved_cards = []
    declined_cards = []
    total_charge = 0.0

    with open(f"{user_id}.txt", "r") as file:
        for line in file.readlines():
            card = line.strip()
            if "|" not in card:
                continue  

            approval_chance = random.randint(1, 100)
            if approval_chance <= APPROVAL_RATE:
                approved_cards.append(card)
                total_charge += CHKKK_COST
            else:
                declined_cards.append(card)

    os.remove(f"{user_id}.txt")  

    response = f"📌 **Card Checking Result:**\n"
    if approved_cards:
        response += f"\n✅ **Approved Cards ($0.50 Charge Each):**\n"
        for card in approved_cards:
            response += f"💳 `{card}`\n"
        response += f"💲 **Total Charge: ${total_charge:.2f}**\n"

    if declined_cards:
        response += f"\n❌ **Declined Cards:**\n"
        for card in declined_cards:
            response += f"💳 `{card}`\n"

    response += f"\n⏳ **Checked At:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    response += f"💬 **Join for More:** [Click Here]({CHANNEL_LINK})"

    bot.reply_to(message, response, parse_mode="Markdown")

bot.polling()
