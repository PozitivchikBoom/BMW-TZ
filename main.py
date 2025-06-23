from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel
from telethon.tl.functions.messages import GetHistoryRequest
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
SESSION_NAME = 'anon_session'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_last_private_chats(client, limit=10):
    dialogs = await client.get_dialogs(limit=100)

    private_chats = []
    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, User) and not entity.bot:
            private_chats.append(dialog)
        if len(private_chats) >= limit:
            break

    return private_chats

async def get_messages_for_last_month(chat, client):
    one_month_ago = datetime.now() - timedelta(days=30)
    messages = []

    async for msg in client.iter_messages(chat, offset_date=None, reverse=True):
        if msg.date < one_month_ago:
            break
        messages.append(msg)

    return messages

async def main():
    await client.start(phone=PHONE)
    print("✅ Авторизовано. Отримуємо чати...")

    chats = await get_last_private_chats(client, limit=10)

    for chat in chats:
        print(f"\n🧾 Чат з: {chat.name or chat.entity.username or chat.entity.phone}")
        messages = await get_messages_for_last_month(chat, client)
        print(f"📩 Повідомлень за останній місяць: {len(messages)}")

        # Можна зберігати ці повідомлення в JSON, CSV або надсилати в AI
        for msg in reversed(messages[-5:]):  # приклад — останні 5
            print(f"{msg.date.strftime('%Y-%m-%d %H:%M')} | {msg.sender_id}: {msg.text}")

with client:
    client.loop.run_until_complete(main())
