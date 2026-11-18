"""
ماژول رصد رویدادهای گروه (Group Events Tracker)

این ماژول هر جوین، لفت و اخراج رو رصد می‌کنه و توی دیتابیس ذخیره می‌کنه.
"""

from telegram import Update
from telegram.ext import MessageHandler, filters


def _make_user_dict(tg_user):
    """ساخت دیکشنری از آبجکت User تلگرام"""
    if not tg_user:
        return None
    return {
        "user_id": tg_user.id,
        "username": tg_user.username or "",
        "first_name": tg_user.first_name or ""
    }


async def new_members_tracker(update, context):
    """رصد اضافه شدن اعضای جدید"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return

    try:
        from database import log_group_event

        # کسی که اعضا رو اضافه کرده
        actor = _make_user_dict(update.effective_user)

        # پیام‌های سرویس (اضافه شدن توسط خود تلگرام)
        if msg.new_chat_members:
            for new_member in msg.new_chat_members:
                if new_member.is_bot:
                    continue
                target = _make_user_dict(new_member)
                # اگه پیام از طرف تلگرام باشه، actor نمیشه تعیین کرد
                # اگه یه نفر اضافه کرده، actor میشه همون
                if update.effective_user and update.effective_user.id != new_member.id:
                    log_group_event(chat.id, "invite", target, actor)
                else:
                    log_group_event(chat.id, "join", target, None)
    except Exception as e:
        print("[NEW MEMBER ERR] " + str(e))


async def left_member_tracker(update, context):
    """رصد خروج یا اخراج اعضا"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return

    try:
        from database import log_group_event
        left = msg.left_chat_member
        if not left:
            return
        if left.is_bot:
            return

        target = _make_user_dict(left)
        actor = _make_user_dict(update.effective_user)

        # اگه خود کاربر خودش رفته (نه اخراج)، actor == target
        if update.effective_user and update.effective_user.id != left.id:
            # یه نفر اخراجش کرده
            log_group_event(chat.id, "kick", target, actor)
        else:
            # خودش لفت داده
            log_group_event(chat.id, "leave", target, None)
    except Exception as e:
        print("[LEFT MEMBER ERR] " + str(e))


def register(app):
    """ثبت هندلرها"""
    # گروه 21 - بعد از شمارش پیام
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_members_tracker),
        group=21
    )
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_tracker),
        group=21
    )
    print("OK module group_events loaded")
