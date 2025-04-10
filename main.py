import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import ContextTypes
from dotenv import load_dotenv
from get_chat_history import fetch_chat_history
from search import semantic_search
import pytz
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import shutil

load_dotenv()
# Define the /test command
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Server is healthy and running!")
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "retry_search":
        await query.edit_message_text("🔄 Please enter a new /find query.")
    
    elif query.data == "help":
        await query.edit_message_text("/find {your vague description} - to recall messages\n")
async def new_member_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        if user.is_bot and user.username == context.bot.username:
            await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hi, I am Codeline bot!\n"
                "You can use the commands to get started:\n"
                "/test - to check if server is running\n"
                "/find {description} - to find your receipts",
            message_thread_id = update.message.message_thread_id
            )
async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    bot = await context.bot.get_me()

    if not context.args:
        await update.message.reply_text("Please enter a description after /find")
        return

    description = " ".join(context.args)

    await context.bot.send_message(
            chat_id=telegram_chat_id,
            text="Gathering chat history... this might take a moment.",
            message_thread_id = thread_id
            )

    #Use Telethon to fetch chat history
    messages = await fetch_chat_history(description, bot.id, telegram_chat_id)
    if not messages:
        await update.message.reply_text("No messages found in the chat.")
    else:
        await context.bot.send_message(
            chat_id=telegram_chat_id,
            text=f'Gathered chat history!\n🔍 Searching for description "{description}"...',
            message_thread_id = thread_id
            )
    
    # Use Qwen search (stub for now)
    result = semantic_search(description, messages)

    if result:
        timestamp = datetime.fromisoformat(result.get("date"))
        sg_time = timestamp.astimezone(pytz.timezone("Asia/Singapore"))
        timestamp = sg_time.strftime("%d %B %Y %H:%M:%S")
        preview = result["text"][:150]
        
        await update.message.reply_text(
            f"💡 Closest match found on *{timestamp}*\n\n\"{preview}\"",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Retry Search", callback_data="retry_search"),
                InlineKeyboardButton("❓ Help", callback_data="help")]]))
    else:
        await update.message.reply_text("No matching messages found.")
async def clear_cache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DOWNLOAD_DIR = "downloads"
    try:
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        with open("message.txt", "w", encoding="utf-8") as f:
            f.write("")  # Clear text file
        await update.message.reply_text("🧹 Memory cleared. All stored messages and media has been removed!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to clear memory: {e}")

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
if not TELEBOT_TOKEN:
    raise ValueError("No Telegram token found, please check .env file")    

# Run the bot
if __name__ == "__main__":

    app = ApplicationBuilder().token(TELEBOT_TOKEN).build()

    app.add_handler(CommandHandler("test", test_command))

    app.add_handler(CommandHandler("find", find_command))

    app.add_handler(CommandHandler("clear", clear_cache))

    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

    