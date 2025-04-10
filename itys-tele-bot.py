from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
load_dotenv()

# Define the /test command
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("this telebot is good to go! server is running now and we are ready to win Alibaba Cloud AI hackathon weeeeee")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No Telegram token found, please check .env file")    
print("TELEGRAM_TOKEN", TELEGRAM_TOKEN)

# Run the bot
if __name__ == "__main__":

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("test", test_command))

    print("🤖 Bot is running...")
    app.run_polling()