import logging
import os
import threading
from flask import Flask
from google import genai
from google.genai import types  # <--- ഇത് ചേർക്കുക
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Render Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Render Dummy Server
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# 1. ഗ്രൂപ്പിൽ പുതിയ ആൾ വരുമ്പോൾ മാത്രം വെൽക്കം ചെയ്യാൻ
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id:
            continue
            
        chat_title = update.effective_chat.title or "Google Play Console Closed Testing"
        user_name = new_user.first_name

        welcome_text = (
            f"Hello {user_name}! 👋\n\n"
            f"Welcome to the <b>{chat_title}</b> group!\n\n"
            f"Glad to have you here. Please share your app details and help each other with testing!"
        )

        await update.message.reply_text(text=welcome_text, parse_mode="HTML")

# 2. ബോട്ടിന്റെ ഇൻബോക്സിൽ (Private Chat) പോയി ചോദിച്ചാൽ മാത്രം AI മറുപടി നൽകാൻ
async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    system_instruction = (
        "You are an expert Google Play Console & Closed Testing assistant for the group 'Google Play Console Closed Testing'. "
        "Your goal is to help developers and testers with Play Console verification, closed testing 14-day rules, "
        "opt-in links, app feedback, and publishing guidelines. Keep responses polite, concise, clear, and helpful."
    )

    try:
        # മോഡൽ gemini-2.0-flash അല്ലെങ്കിൽ gemini-1.5-flash ഉപയോഗിക്കുക
        response = ai_client.models.generate_content(
            model='gemini-3.7-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("എനിക്ക് മറുപടി നൽകാൻ കഴിഞ്ഞില്ല, ദയവായി വീണ്ടും ശ്രമിക്കൂ.")
        
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        await update.message.reply_text("Sorry, I encountered an error. Please try again later.")

def main():
    threading.Thread(target=run_flask).start()

    app = Application.builder().token(BOT_TOKEN).build()

    # ഗ്രൂപ്പിൽ പുതിയ ആൾക്കാരെ വെൽക്കം ചെയ്യാൻ ഉള്ള ഹാൻഡ്‌ലർ
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member)
    )
    
    # ബോട്ടിന്റെ direct inbox/chat-ൽ അയക്കുന്ന മെസ്സേജുകൾക്ക് മാത്രം AI മറുപടി
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, ai_chat_handler)
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
