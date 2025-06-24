from telethon.sync import TelegramClient
from dotenv import load_dotenv
import asyncio
import os

from chat_parser import save_chats_history
from analysis import analyze_promises

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
SESSION_NAME = 'anon_session'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    await client.start(phone=PHONE)
    print("✅ Авторизовано")

    await save_chats_history(client)   # <--- зчитує чати
    analyze_promises()                 # <--- запускає аналіз

with client:
    client.loop.run_until_complete(main())
