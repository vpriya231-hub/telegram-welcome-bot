import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# നിങ്ങളുടെ BotFather API Token
BOT_TOKEN = "8830828939:AAHEhz-yfrpsqplTl_XxtZ-duZbxUD62iC0"

# Render Port Scan error ഒഴിവാക്കാൻ ഉള്ള Dummy Server
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member

    if (
        result.old_chat_member.status == update.chat_member.status.LEFT
        and result.new_chat_member.status == update.chat_member.status.MEMBER
    ):
        new_user = result.new_chat_member.user
        chat_title = "Google Playconsole Closed Testing"
        user_name = new_user.first_name

        welcome_text = (
            f"Hello {user_name}! 👋\n\n"
            f"Welcome to the <b>{chat_title}</b> group!\n\n"
            f"Glad to have you here. Please share your app details and help each other with testing!"
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=welcome_text, 
            parse_mode="HTML"
        )

def main():
    # Background-ൽ ഫേക്ക് വെബ് സെർവർ സ്റ്റാർട്ട് ചെയ്യുന്നു
    threading.Thread(target=run_flask).start()

    # Telegram Bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(
        ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER)
    )
    app.run_polling(allowed_updates=Update.CHAT_MEMBER)

if __name__ == "__main__":
    main()
