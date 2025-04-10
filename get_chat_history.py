# fetch_chat_history.py
from telethon.tl.types import MessageMediaPhoto
from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv
import hashlib
load_dotenv()


api_id = os.getenv("TELEAPP_API_ID")
api_hash = os.getenv("TELEAPP_API_HASH")
# print(f"API ID: {api_id}")
# print(f"API Hash: {api_hash}")

# Creating a session file 'user_session.session'
client = TelegramClient("user_session", api_id, api_hash)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def save_messages_to_txt(messages, output_path="message.txt"):
    with open(output_path, "w", encoding="utf-8") as f:
        for msg in messages:
            clean_msg = { #
                "id": msg["id"],
                "text": msg["text"].strip(),
                "date": msg["date"],
                "sender_id": msg["sender_id"]
                # "media_file": msg["media_file"] # exclude media file for now
            }
            f.write(str(clean_msg) + "\n")
            # f.write(msg["text"].strip() + "\n")
async def fetch_chat_history(desc: str, bot_id: int, chat_id: int, limit: int = 1000):
    messages = []

    async with client:
        me = await client.get_me()
        print("Logged in as:", me.username, "(Bot:", me.bot, ")")
        entity = await client.get_entity(chat_id)

        async for msg in client.iter_messages(entity, limit=limit):
            content = ""
            media_file_path = None

            #Check if the message contains media
            if msg.media:
                media_type = "media"
                if isinstance(msg.media, MessageMediaPhoto):
                    media_type = "photo"
                elif msg.voice:
                    media_type = "voice"
                elif msg.audio:
                    media_type = "audio"
                elif msg.video:
                    media_type = "video"
                elif msg.document:
                    media_type = "document"

                ext = ".bin"  # fallback
                if msg.file and msg.file.ext:
                    ext = msg.file.ext

                filename = f"{media_type}_{msg.id}{ext}"
                file_path = os.path.join(DOWNLOAD_DIR, filename)

                #Only download if not already saved
                if not os.path.exists(file_path):
                    media_file_path = await msg.download_media(file=file_path)
                else:
                    media_file_path = file_path

                if media_file_path:
                    content += f"[{os.path.basename(media_file_path)}]"

            if msg.sender_id == bot_id:
                    continue #exlude bot messages
            else:
                if msg.text and not msg.text.lower().startswith("/find") and not msg.text.lower().startswith("/clear") and not msg.text.lower().startswith("/test"): #and not msg.text.startswith("Gathering chat history"):
                    content += msg.text.strip()
                #elif msg.reply_to_msg_id: #and not msg.text.startswith("/find"):
                #   content += f"[reply to {msg.reply_to_msg_id}] {msg.text}"

                if content:
                    messages.append({
                        "id": msg.id,
                        "text": content,
                        "date": str(msg.date),
                        "sender_id": hashlib.sha256(str(msg.sender_id).encode()).hexdigest()[:10],
                        "media_file": media_file_path
                    })

    save_messages_to_txt(messages)
    
    return messages