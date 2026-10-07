import asyncio
import logging
import os
import threading
from flask import Flask
from google import genai
from google.genai import types
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

# Render Dummy Server to keep instance active
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# 1. Welcome handler for new group members
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

# 2. AI chat handler for direct private messages
async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Send typing action to Telegram chat
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    system_instruction = (
        "You are the official AI assistant representing 'V Astra AI Technologies' and the 'Google Play Console Closed Testing' community.\n\n"
        "Core Guidelines:\n"
        "1. Brand & Apps: When users ask about your apps, products, or downloads, share these official details and links:\n"
        "   - V Astra AI:\n"
        "     * Google Play Store: https://play.google.com/store/apps/details?id=com.vastraai.app\n"
        "     * Microsoft Store: https://apps.microsoft.com/store/detail/9NR87WK2VV23?cid=DevShareMCLPCS\n"
        "   - AI Prompt Library:\n"
        "     * Google Play Store: https://play.google.com/store/apps/details?id=com.aipromptlibrary.app\n"
        "     * Microsoft Store: https://apps.microsoft.com/store/detail/9NG0RZG8N24D?cid=DevShareMCLPCS\n\n"
        "2. Support Contact: If anyone asks for support, developer contact, reporting issues, or feedback, provide the official email: supportvastra@gmail.com.\n\n"
        "3. Google Play Console & Closed Testing: Assist developers and testers with Play Console verification, closed testing 14-day rules, opt-in links, testing feedback, and publishing guidelines.\n\n"
        "4. General Chat: Handle general friendly conversations, questions, and tech queries naturally and politely.\n\n"
        "Keep responses neat, accurate, concise, and helpful."
    )

    try:
        # Run blocking generate_content call asynchronously to avoid freezing the event loop
        response = await asyncio.to_thread(
            ai_client.models.generate_content,
            model='gemini-3.7-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("I could not generate a response. Please try again.")
        
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        await update.message.reply_text("Sorry, I encountered an error. Please try again later.")

def main():
    threading.Thread(target=run_flask).start()

    app = Application.builder().token(BOT_TOKEN).build()

    # Handler to welcome new users joining the group
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member)
    )
    
    # Handler for private direct chat messages only
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, ai_chat_handler)
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
