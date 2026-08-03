import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# നിങ്ങളുടെ BotFather API Token
BOT_TOKEN = "8830828939:AAHEhz-yfrpsqplTl_XxtZ-duZbxUD62iC0"

# Render Port Scan error ഒഴിവാക്കാനുള്ള Flask Server
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# പുതിയ അംഗങ്ങൾ വരുമ്പോൾ പ്രവർത്തിക്കുന്ന ഫങ്ഷൻ
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # പുതിയതായി വന്ന യൂസർമാരെ കണ്ടുപിടിക്കുന്നു
    for new_user in update.message.new_chat_members:
        # ബോട്ട് തന്നെയാണ് ഗ്രൂപ്പിൽ ആഡ് ആയതെങ്കിൽ വെൽക്കം മെസ്സേജ് അയക്കേണ്ടതില്ല
        if new_user.id == context.bot.id:
            continue
            
        chat_title = update.effective_chat.title or "Google Playconsole Closed Testing"
        user_name = new_user.first_name

        welcome_text = (
            f"Hello {user_name}! 👋\n\n"
            f"Welcome to the <b>{chat_title}</b> group!\n\n"
            f"Glad to have you here. Please share your app details and help each other with testing!"
        )

        await update.message.reply_text(text=welcome_text, parse_mode="HTML")

def main():
    # Flask Server ബാക്ക്ഗ്രൗണ്ടിൽ സ്റ്റാർട്ട് ചെയ്യുന്നു
    threading.Thread(target=run_flask).start()

    # Telegram Bot Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Supergroup-ൽ പുതിയ മെമ്പേഴ്സ് വരുമ്പോൾ ട്രാക്ക് ചെയ്യാൻ MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS) ഉപയോഗിക്കുന്നു
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member)
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

