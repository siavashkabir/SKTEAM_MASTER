import asyncio
import sqlite3
from telegram import Bot
from config import BOT_TOKEN, DATABASE_PATH
from database import queue_userbot_join

USERBOT_ID = 8250087472


async def trigger():
    bot = Bot(token=BOT_TOKEN)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id, title FROM groups")
    groups = c.fetchall()
    conn.close()

    print(f"═══ {len(groups)} گروه ═══")
    print()

    for cid, title in groups:
        print(f"── {title} ({cid}) ──")
        try:
            # چک کن userbot عضوه
            try:
                ub = await bot.get_chat_member(cid, USERBOT_ID)
                if ub.status not in ("left", "kicked"):
                    print(f"  ✅ userbot عضوه ({ub.status})")
                    if ub.status == "member":
                        print(f"  → promote می‌کنم")
                        try:
                            await bot.promote_chat_member(
                                chat_id=cid,
                                user_id=USERBOT_ID,
                                can_delete_messages=True,
                                can_restrict_members=True,
                                can_pin_messages=True,
                                can_invite_users=True,
                                can_change_info=False,
                                can_promote_members=False,
                                can_manage_video_chats=True,
                                can_manage_chat=False,
                                is_anonymous=False,
                            )
                            print(f"  ✅ promote شد")
                        except Exception as e:
                            print(f"  ❌ promote: {e}")
                    continue
            except Exception:
                pass

            # نیست → لینک بساز
            print(f"  ⚠️ userbot نیست → لینک invite می‌سازم")
            try:
                link = await bot.create_chat_invite_link(
                    chat_id=cid,
                    name=f"Userbot Auto {cid}",
                    member_limit=1,
                )
                print(f"  ✅ لینک: {link.invite_link}")
                req_id = queue_userbot_join(cid, link.invite_link)
                if req_id:
                    print(f"  ✅ queue شد (id={req_id})")
                    print(f"  → userbot_service خودش join می‌شه")
                else:
                    print(f"  ⚠️ قبلاً queue شده")
            except Exception as e:
                print(f"  ❌ لینک: {e}")

        except Exception as e:
            print(f"  ❌: {e}")
        print()
        await asyncio.sleep(2)

    await bot.close()


asyncio.run(trigger())
