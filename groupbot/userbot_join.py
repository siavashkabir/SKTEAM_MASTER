import asyncio
import sys
sys.path.insert(0, '.')

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION


async def join_group(invite_link):
    app = Client(name="userbot_join", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    await app.start()
    
    try:
        # لینک رو parse کن
        if "+" in invite_link:
            hash_part = invite_link.split("+")[-1].split("/")[-1]
        elif "joinchat" in invite_link:
            hash_part = invite_link.split("/")[-1]
        else:
            hash_part = invite_link.split("/")[-1]
        
        print(f"🔗 جوین می‌شم با hash: {hash_part}")
        chat = await app.join_chat(hash_part)
        print(f"✅ عضو شدم: {chat.title} (id={chat.id})")
    except Exception as e:
        print(f"❌ خطا: {e}")
    
    await app.stop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("استفاده: python3 userbot_join.py <invite_link>")
        sys.exit(1)
    _loop.run_until_complete(join_group(sys.argv[1]))
