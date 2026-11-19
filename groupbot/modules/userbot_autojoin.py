"""Auto: وقتی ربات به گروه جدید می‌ره، userbot رو با invite link میاره + ادمینش می‌کنه."""
import asyncio
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

USERBOT_ID = 8250087472
USERBOT_USERNAME = "Skmusic001"


async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.new_chat_members:
        return
    if chat.type not in ("group", "supergroup"):
        return

    bot_id = context.bot.id
    if not any(m.id == bot_id for m in msg.new_chat_members):
        return

    print(f"[AUTOJOIN] ربات به {chat.id} ({chat.title}) اضافه شد")
    await asyncio.sleep(3)

    # چک کن userbot از قبل عضوه
    userbot_in = False
    try:
        ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
        if ub.status not in ("left", "kicked"):
            userbot_in = True
            print(f"[AUTOJOIN] userbot از قبل عضوه ({ub.status})")
    except Exception:
        pass

    if not userbot_in:
        # ★ لینک invite بساز + queue کن
        try:
            from database import queue_userbot_join
            link = await context.bot.create_chat_invite_link(
                chat_id=chat.id,
                name=f"Userbot Join {chat.id}",
                member_limit=1,
            )
            print(f"[AUTOJOIN] لینک ساخته شد: {link.invite_link}")
            req_id = queue_userbot_join(chat.id, link.invite_link)
            if req_id:
                print(f"[AUTOJOIN] queue شد (id={req_id})")
                try:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="⏳ در حال فعال‌سازی دستیار گروه..."
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"[AUTOJOIN] لینک خطا: {e}")

    # اگه userbot عضو بود ولی ادمین نبود، promote کن
    if userbot_in:
        try:
            ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
            if ub.status == "member":
                await context.bot.promote_chat_member(
                    chat_id=chat.id,
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
                print(f"[AUTOJOIN] ✅ userbot promote شد")
        except Exception as e:
            print(f"[AUTOJOIN PROMOTE ERR] {e}")


async def auto_promote_job(context: ContextTypes.DEFAULT_TYPE):
    """job دوره‌ای: چک کن userbot عضوه ولی ادمین نیست → promote"""
    try:
        import turso_db as sqlite3
        from config import DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM groups")
        chats = [r[0] for r in c.fetchall()]
        conn.close()

        for cid in chats:
            try:
                ub = await context.bot.get_chat_member(cid, USERBOT_ID)
                if ub.status == "member":
                    await context.bot.promote_chat_member(
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
                    print(f"[AUTOPROMOTE JOB] userbot در {cid} promote شد")
                    try:
                        await context.bot.send_message(
                            chat_id=cid,
                            text="✅ دستیار گروه فعال شد."
                        )
                    except Exception:
                        pass
            except Exception:
                pass
            await asyncio.sleep(3)
    except Exception as e:
        print(f"[AUTOPROMOTE JOB ERR] {e}")


def register(app):
    # handler
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            on_bot_added,
            block=False
        ),
        group=-8
    )
    # job دوره‌ای هر ۳۰ ثانیه
    if hasattr(app, 'job_queue') and app.job_queue:
        app.job_queue.run_repeating(auto_promote_job, interval=30, first=10)
        print("OK userbot_autojoin job registered")
    print("OK module userbot_autojoin loaded")
