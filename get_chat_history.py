# fetch_chat_history.py

from telethon.sync import TelegramClient
from telethon.tl.types import PeerChat
import os
from dotenv import load_dotenv
load_dotenv()


api_id = os.getenv("TELEAPP_API_ID")
api_hash = os.getenv("TELEAPP_API_HASH")
# print(f"API ID: {api_id}")
# print(f"API Hash: {api_hash}")

# Creating a session file 'user_session.session'
client = TelegramClient("user_session", api_id, api_hash)

async def fetch_chat_history(desc: str, chat_id: int, limit: int = 1000):
    messages = []

    async with client:
        me = await client.get_me()
        print("Logged in as:", me.username, "(Bot: ", me.bot, ")")
        entity = await client.get_entity(chat_id)

        async for msg in client.iter_messages(entity, limit=limit):
            content = ""
            if msg.text and msg.text.strip() != f"/find {desc}":
                if not msg.text.startswith("Gathered chat history!"):
                    content += msg.text
            if msg.photo:
                content += " [Photo]"
            if msg.video:
                content += " [Video]"
            if msg.voice or msg.audio:
                content += " [Audio]"
            if msg.sticker:
                content += " [Sticker]"
            if msg.reply_to_msg_id:
                content += f" [reply to {msg.reply_to_msg_id}]"

            if content:
                messages.append({
                    "id": msg.id,
                    "text": content.strip(),
                    "date": str(msg.date),
                    "sender_id": msg.sender_id,
                })

    return messages