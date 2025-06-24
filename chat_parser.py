from telethon.tl.types import User
import json
import os

async def get_last_private_chats(client, limit=10):
    dialogs = await client.get_dialogs(limit=100)
    private_chats = [d for d in dialogs if isinstance(d.entity, User) and not d.entity.bot]
    return private_chats[:limit]

async def get_messages_from_chat(client, chat, limit=300):
    messages = []
    async for msg in client.iter_messages(chat.id, limit=limit):
        messages.append({
            "sender_id": msg.sender_id,
            "text": msg.message,
            "date": msg.date.isoformat() if msg.date else None
        })
    return messages

async def save_chats_history(client, out_path="data/chat_history.json"):
    os.makedirs("data", exist_ok=True)

    chats = await get_last_private_chats(client)
    history = {}

    for chat in chats:
        print(f"📥 Завантажую історію з {getattr(chat.entity, 'first_name', '')} {getattr(chat.entity, 'last_name', '')}".strip() + "...")
        messages = await get_messages_from_chat(client, chat)
        history[str(chat.id)] = {
            "username": getattr(chat.entity, "username", None),
            "name": f"{getattr(chat.entity, 'first_name', '')} {getattr(chat.entity, 'last_name', '')}".strip(),
            "messages": messages
        }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"✅ Історію збережено в {out_path}")
