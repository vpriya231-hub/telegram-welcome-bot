import logging
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# -------------------------------------------------------------
# നിങ്ങളുടെ BotFather API Token താഴെ നൽകുക
# -------------------------------------------------------------
BOT_TOKEN = "8830828939:AAHEhz-yfrpsqplTl_XxtZ-duZbxUD62iC0"


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member

    # പുതിയ മെമ്പർ ജോയിൻ ചെയ്യുമ്പോൾ മാത്രം വർക്ക് ചെയ്യാൻ
    if (
        result.old_chat_member.status == update.chat_member.status.LEFT
        and result.new_chat_member.status == update.chat_member.status.MEMBER
    ):
        new_user = result.new_chat_member.user
        
        # ഗ്രൂപ്പിന്റെ പേര്
        chat_title = "Google Playconsole Closed Testing"
        
        # ടെലിഗ്രാമിലെ ആളുടെ പേര് എടുക്കുന്നു (First Name)
        user_name = new_user.first_name

        # വെൽക്കം മെസ്സേജിൽ പേര് ഉൾപ്പെടുത്തിയിരിക്കുന്നു
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
    print("Starting bot from Mobile...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER)
    )

    print("Bot is alive and listening!")
    app.run_polling(allowed_updates=Update.CHAT_MEMBER)


if __name__ == "__main__":
    main()

