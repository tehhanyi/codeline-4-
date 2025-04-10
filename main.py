import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import ContextTypes
from dotenv import load_dotenv
from get_chat_history import fetch_chat_history
from search import semantic_search

load_dotenv()

# Define the /test command
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Server is healthy and running!")
async def new_member_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        if user.is_bot and user.username == context.bot.username:
            await update.message.reply_text(
                "Hi, I am Codeline bot!\n"
                "You can use the commands to get started:\n"
                "/test - to check if server is running\n"
                "/find {description} - to find your receipts"
            )

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please enter a description after /find")
        return

    description = " ".join(context.args)

    await update.message.reply_text("🔍 Searching messages... this might take a moment.")

    # (Step 1) Extract chat ID
    telegram_chat_id = update.effective_chat.id

    # (Step 2) Use Telethon to fetch messages
    messages = await fetch_chat_history(telegram_chat_id)
    if not messages:
        await update.message.reply_text("No messages found in the chat.")
    else:
        await update.message.reply_text(f"Gathered chat history, now searching for text description: \"{description}\"...")

    # (Step 3) Use Qwen search (stub for now)
    result = semantic_search(description, messages)

    if result:
       await update.message.reply_text(f"💡 Closest match to your query:",reply_to_message_id=result["id"]
)
    else:
        await update.message.reply_text("No matching messages found.")

TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")
if not TELEBOT_TOKEN:
    raise ValueError("No Telegram token found, please check .env file")    

# Run the bot
if __name__ == "__main__":

    app = ApplicationBuilder().token(TELEBOT_TOKEN).build()

    app.add_handler(CommandHandler("test", test_command))

    app.add_handler(CommandHandler("find", find_command))


    print("🤖 Bot is running...")
    app.run_polling()