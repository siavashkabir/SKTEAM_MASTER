from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from database import (
    set_nickname, get_nickname, delete_nickname, is_nickname_enabled, toggle_nickname,
    set_profile, get_profile, delete_profile,
    is_bot_admin, is_group_owner
)
from config import OWNER_ID
import random


# ========== جواب‌های متنوع برای صدا زدن ربات ==========
NICKNAME_REPLIES = [
    "جانم {nick} عزیز! 😍",
    "بله {nick} خان؟ 😎",
    "چشم {nick} جان! 🌹",
    "در خدمتم {nick} عزیز! 💫",
    "بفرمایید {nick} جان! ✨",
    "قربانت {nick}! 🌸",
    "بله بله {nick} جان! 😄",
    "ای جانم {nick}! 🥰",
    "چیه {nick}؟ چاکرم! 🙋‍♂️",
    "بله قربان {nick}! 🫡",
    "ای بابا {nick} جان، باز چی شده؟ 😂",
    "جونم {nick}؟ 💖",
    "ها؟ چی گفتی {nick}؟ 👂",
    "بله دیگه {nick}، گوش به فرمانم! ⚔️",
    "چشم {nick} عزیز، هر چی بگی! 🌟",
    "قربون دستت {nick}! 🙌",
    "ای جانم، {nick} صدام زد! 😻",
    "بله {nick} جان، در خدمتم! 🎩",
    "چاکریم {nick}! 🧎",
    "بفرما {nick} جان، چی امر داری؟ 📋",
    "جون به لبم رسید {nick}! 😂",
    "آخیش، {nick} یادم کرد! 😌",
    "بله {nick} خان، بنده در خدمتم! 🎖️",
    "قربونت برم {nick}! 💐",
    "چشم {nick}، ولی اینبار سریع بگو! ⏰",
    "ای {nick}، تو هم پیدات شد! 🙃",
    "بله {nick} عزیز، سلام! 🤝",
    "جونم {nick}؟ چی می‌خوای؟ 🤔",
    "حاجی {nick}، بفرما! 🕌",
    "سرباز {nick}، در خدمتم! 🎯",
    "بله {nick} جان، چاکریم! 🌺",
    "قربان {nick}، اختیار دارید! 👑",
    "ای {nick}، باز چی گفتی؟ 😅",
    "بله بله {nick} جان، بگو ببینم! 👀",
    "چشم {nick}، ولی سریع باش! ⚡",
    "جون {nick}، بفرما! 💕",
    "بله {nick} خان، سلام عرض کردم! 🙇",
    "قربون صدقه‌ت برم {nick}! 💋",
    "ای {nick}، تو دیگه کی هستی؟ 😜",
    "بله {nick}، بنده گوش به فرمانم! 📻",
    "چاکر {nick}، در خدمتم! 🧤",
    "جونم {nick}، چی شده؟ 🩺",
    "بله {nick} عزیز، چطور می‌تونم کمک کنم؟ 🤲",
    "ای {nick}، دلم برات تنگ شده بود! 🥺",
    "چشم {nick}، ولی اینبار به خدا! 🤲",
    "قربان {nick}، امر بفرما! 🎺",
    "بله {nick} جان، در خدمتیم! 🛎️",
    "جون {nick}، سلام! 😊",
    "ای {nick}، تو هم اینجایی؟ 😲",
    "بله {nick}، بنده حاضر! 🧑‍✈️",
    "چاکریم {nick} جان، بفرما! 🥂",
]

# ========== جواب‌های متنوع برای ثبت لقب ==========
NICKNAME_SET_REPLIES = [
    "✅ لقب «{nick}» برای {name} تنظیم شد! 🎉",
    "✅ از این به بعد {name} رو با لقب «{nick}» صدا می‌زنیم! 😎",
    "✅ ثبت شد! {name} = «{nick}» 📝",
    "✅ لقب «{nick}» به {name} چسبید! 🏷️",
    "✅ تمام! {name} از این به بعد «{nick}» هست! 🌟",
    "✅ به به! {name} با لقب «{nick}» خوشگل شد! 😍",
    "✅ ثبت شد برادر! {name} = «{nick}» ✅",
    "✅ لقب «{nick}» رسماً به {name} تعلق گرفت! 🎖️",
    "✅ اوکی! {name} از این لحظه «{nick}» خطاب میشه! 📢",
    "✅ انجام شد! {name} عزیز، لقب جدیدت «{nick}» هست! 💝",
]

# ========== جواب‌های متنوع برای حذف لقب ==========
NICKNAME_DEL_REPLIES = [
    "✅ لقب {name} حذف شد.",
    "✅ از این به بعد {name} بدون لقب صدا زده می‌شه! 🗑️",
    "✅ پاک شد! {name} دوباره بی‌لقب شد! 😅",
    "✅ لقب {name} پاک شد، ولی چرا؟! 🤔",
    "✅ تمام! {name} از این به بعد بدون لقب! 🧹",
    "✅ حذف شد! {name} عزیز، لقبت رفت! 🫡",
]

# ========== جواب‌های متنوع برای تایید اصل ==========
PROFILE_APPROVE_REPLIES = [
    "✅ اصل {name} تایید و ذخیره شد.",
    "✅ ثبت شد! اصل {name} حالا توی دیتابیس ما هست! 📚",
    "✅ تایید شد! {name} دیگه رسماً شناخته شده! 🪪",
    "✅ اوکی! اصل {name} تایید و ثبت شد! 🎯",
    "✅ عالی! مشخصات {name} ثبت شد! 📋",
    "✅ تایید شد برادر! {name} توی لیست ما هست! 📝",
]


# ========== دستورات ==========

async def set_nickname_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if not (is_group_owner(chat.id, user.id) or is_bot_admin(user.id) or user.id == OWNER_ID):
        await msg.reply_text("⛔ فقط مالک گروه می‌تواند لقب تعیین کند.")
        return
    
    # حالت اول: ریپلای
    if msg.reply_to_message and msg.reply_to_message.from_user:
        parts = msg.text.split(maxsplit=2)
        if len(parts) < 3:
            await msg.reply_text("📝 لطفاً به این شکل بنویسید:\n`تنظیم لقب <لقب>` (با ریپلای)")
            return
        nickname = parts[2].strip()
        target = msg.reply_to_message.from_user
        set_nickname(chat.id, target.id, nickname)
        reply = random.choice(NICKNAME_SET_REPLIES).format(nick=nickname, name=target.first_name)
        await msg.reply_text(reply)
        return
    
    # حالت دوم: با یوزرنیم
    parts = msg.text.split()
    if len(parts) >= 3:
        username_part = None
        nickname_part = None
        for i, p in enumerate(parts):
            if p.startswith("@"):
                username_part = p.replace("@", "")
                if i + 1 < len(parts):
                    nickname_part = " ".join(parts[i+1:])
                break
        
        if username_part and nickname_part:
            try:
                admins = await chat.get_administrators()
                found = None
                for admin in admins:
                    if admin.user.username and admin.user.username.lower() == username_part.lower():
                        found = admin.user
                        break
                if found:
                    set_nickname(chat.id, found.id, nickname_part)
                    reply = random.choice(NICKNAME_SET_REPLIES).format(nick=nickname_part, name=found.first_name)
                    await msg.reply_text(reply)
                    return
            except Exception:
                pass
            await msg.reply_text(f"❌ کاربری با یوزرنیم @{username_part} توی ادمین‌ها پیدا نشد.\n(فعلاً فقط ادمین‌ها قابل جستجو هستند)")
            return
    
    await msg.reply_text("📝 لطفاً به این شکل بنویسید:\n`تنظیم لقب <لقب>` (با ریپلای)\nیا\n`تنظیم لقب @username <لقب>`")


async def delete_nickname_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if not (is_group_owner(chat.id, user.id) or is_bot_admin(user.id) or user.id == OWNER_ID):
        await msg.reply_text("⛔ فقط مالک گروه می‌تواند لقب را حذف کند.")
        return
    
    # حالت اول: ریپلای
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target = msg.reply_to_message.from_user
        delete_nickname(chat.id, target.id)
        reply = random.choice(NICKNAME_DEL_REPLIES).format(name=target.first_name)
        await msg.reply_text(reply)
        return
    
    # حالت دوم: با یوزرنیم
    parts = msg.text.split()
    if len(parts) >= 2 and parts[1].startswith("@"):
        username_part = parts[1].replace("@", "")
        try:
            admins = await chat.get_administrators()
            found = None
            for admin in admins:
                if admin.user.username and admin.user.username.lower() == username_part.lower():
                    found = admin.user
                    break
            if found:
                delete_nickname(chat.id, found.id)
                reply = random.choice(NICKNAME_DEL_REPLIES).format(name=found.first_name)
                await msg.reply_text(reply)
                return
        except Exception:
            pass
        await msg.reply_text(f"❌ کاربری با یوزرنیم @{username_part} پیدا نشد.")
        return
    
    await msg.reply_text("📝 لطفاً روی پیام کاربر ریپلای بزنید یا بنویسید:\n`حذف لقب @username`")


async def approve_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if not (is_group_owner(chat.id, user.id) or is_bot_admin(user.id) or user.id == OWNER_ID):
        await msg.reply_text("⛔ فقط مالک و ادمین‌ها می‌توانند تایید اصل کنند.")
        return
    
    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text("📝 لطفاً روی پیام مشخصات کاربر ریپلای بزنید.")
        return
    
    target = msg.reply_to_message.from_user
    raw_text = msg.reply_to_message.text or msg.reply_to_message.caption or ""
    
    if not raw_text.strip():
        await msg.reply_text("❌ پیام ریپلای‌شده متنی برای ذخیره ندارد.")
        return
    
    set_profile(chat.id, target.id, raw_text, user.id)
    reply = random.choice(PROFILE_APPROVE_REPLIES).format(name=target.first_name)
    await msg.reply_text(reply)


async def show_my_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    profile = get_profile(chat.id, user.id)
    if not profile:
        await msg.reply_text("❌ هنوز اصل شما تایید نشده است.")
        return
    
    raw_text, approved_by, approved_at = profile
    await msg.reply_text(f"👤 مشخصات شما:\n\n{raw_text}")


async def show_other_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text("📝 لطفاً روی پیام کاربر ریپلای بزنید یا بنویسید «اصل من».")
        return
    
    target = msg.reply_to_message.from_user
    profile = get_profile(chat.id, target.id)
    if not profile:
        await msg.reply_text(f"❌ اصل {target.first_name} تایید نشده است.")
        return
    
    raw_text, approved_by, approved_at = profile
    await msg.reply_text(f"👤 مشخصات {target.first_name}:\n\n{raw_text}")


async def delete_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if not (is_group_owner(chat.id, user.id) or is_bot_admin(user.id) or user.id == OWNER_ID):
        await msg.reply_text("⛔ فقط مالک و ادمین‌ها می‌توانند حذف اصل کنند.")
        return
    
    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text("📝 لطفاً روی پیام کاربر ریپلای بزنید.")
        return
    
    target = msg.reply_to_message.from_user
    delete_profile(chat.id, target.id)
    await msg.reply_text(f"✅ اصل {target.first_name} حذف شد.")


def register(app):
    # دستورات انگلیسی برای تلگرام (با /)
    app.add_handler(CommandHandler("setnick", set_nickname_cmd), group=5)
    app.add_handler(CommandHandler("delnick", delete_nickname_cmd), group=5)
    app.add_handler(CommandHandler("approve", approve_profile_cmd), group=5)
    app.add_handler(CommandHandler("meprofile", show_my_profile_cmd), group=5)
    app.add_handler(CommandHandler("profile", show_other_profile_cmd), group=5)
    app.add_handler(CommandHandler("delprofile", delete_profile_cmd), group=5)
    
    # دستورات فارسی برای پیام‌های متنی (بدون /) - توی گروه 5
    app.add_handler(MessageHandler(filters.Regex(r"^تنظیم لقب\s+.+$"), set_nickname_cmd), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^حذف لقب$"), delete_nickname_cmd), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^تایید اصل$"), approve_profile_cmd), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^اصل من$"), show_my_profile_cmd), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^اصل$"), show_other_profile_cmd), group=5)
    app.add_handler(MessageHandler(filters.Regex(r"^حذف اصل$"), delete_profile_cmd), group=5)
