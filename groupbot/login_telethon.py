#!/usr/bin/env python3
"""ساخت Telethon String Session با login تعاملی"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from userbot_config import API_ID, API_HASH


async def main():
    print("=" * 50)
    print("🔐 Telethon Login")
    print("=" * 50)
    print()
    print(f"API_ID: {API_ID}")
    print()
    
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print()
    print("=" * 50)
    print(f"✅ Login موفق!")
    print(f"   نام: {me.first_name}")
    print(f"   یوزرنیم: @{me.username}")
    print(f"   ID: {me.id}")
    print("=" * 50)
    print()
    
    session_string = client.session.save()
    
    print("📋 SESSION STRING (این رو کپی کن):")
    print()
    print(session_string)
    print()
    print("=" * 50)
    
    # ذخیره توی فایل
    with open("telethon_session.txt", "w") as f:
        f.write(session_string)
    print("✅ ذخیره شد توی: telethon_session.txt")
    print("=" * 50)
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
