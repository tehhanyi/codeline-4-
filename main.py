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
    telegram_chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id

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
    messages = await fetch_chat_history(description, telegram_chat_id)
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
        timestamp = result.get("date")
        preview = result["text"][:150]
        
        await update.message.reply_text(
            f"💡 Closest match found from *{timestamp}*:\n\n\"{preview}...\"",
            parse_mode="Markdown"
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