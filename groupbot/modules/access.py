from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import (
    ADMIN_PERMS, VIP_PERMS, DEPUTY_PERMS,
    is_bot_admin, is_admin, is_group_owner, is_deputy, is_vip, get_group_owner,
    get_user_perms, toggle_user_perm, get_all_deputy_perms, has_user_perm,
    toggle_deputy_perm
)
from config import OWNER_ID

NL = chr(10)
ACCESS_CHANGED = {}  # state موقت برای دکمه تایید



def display_user(user):
    name = user.first_name or "کاربر"
    if user.username:
        return name + " (@" + user.username + ")"
    return name


async def is_bot_owner_or_admin(user_id):
    try:
        if user_id == OWNER_ID:
            return True
        if is_bot_admin(user_id):
            return True
    except Exception:
        pass
    return False


async def can_manage_access(chat, user_id):
    """کی می تونه از دستور دسترسی استفاده کنه؟
    - سازنده ربات
    - ادمین های ربات (سودو)
    - مالک گروه (تعیین شده)
    - سازنده واقعی گروه (creator تلگرام)
    """
    if await is_bot_owner_or_admin(user_id):
        return True
    try:
        if is_group_owner(chat.id, user_id):
            return True
    except Exception:
        pass
    try:
        m = await chat.get_member(user_id)
        if m.status == "creator":
            return True
    except Exception:
        pass
    return False


def get_target_role(chat_id, user_id):
    """تشخیص دقیق نقش کاربر هدف"""
    try:
        if user_id == OWNER_ID:
            return "bot_owner"
        if is_bot_admin(user_id):
            return "bot_admin"
        if is_group_owner(chat_id, user_id):
            return "group_owner"
        # ★ چک ادمین (قبل از معاون)
        if is_admin(chat_id, user_id):
            return "admin"
        if is_deputy(chat_id, user_id):
            return "deputy"
        if is_vip(chat_id, user_id):
            return "vip"
    except Exception:
        pass
    return "member"


def role_label(role):
    labels = {
        "bot_owner": "سازنده ربات",
        "bot_admin": "ادمین ربات (سودو)",
        "group_owner": "مالک گروه",
        "admin": "مدیر گروه",
        "deputy": "معاون گروه",
        "vip": "عضو ویژه (VIP)",
        "member": "عضو عادی",
    }
    return labels.get(role, "نامشخص")


def role_emoji(role):
    labels = {
        "bot_owner": "👑",
        "bot_admin": "⭐",
        "group_owner": "🎩",
        "deputy": "🛡",
        "vip": "🌟",
        "member": "👤",
    }
    return labels.get(role, "")


def build_access_menu(uid, chat_id, target_id, target_name, role, is_bot_owner_user=False):
    """ساخت منوی دسترسی بر اساس نقش کاربر"""
    # مالک/سودو ربات → پیام
    if role in ("bot_owner", "bot_admin"):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(role_emoji(role) + " " + role_label(role) + " (ربات)", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("⚠️ مدیریت این بخش فقط توسط مالک ربات امکان‌پذیر است", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))],
        ])

    keyboard = []
    keyboard.append([InlineKeyboardButton(role_emoji(role) + " " + role_label(role), callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
    

    # مالک گروه یا معاون → DEPUTY_PERMS
    if role in ("group_owner", "deputy"):
        perms = get_all_deputy_perms(chat_id)
        if not perms:
            perms = {k: True for k, _ in DEPUTY_PERMS}
        keyboard.append([InlineKeyboardButton("👤 مدیریت گروه / معاون", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in DEPUTY_PERMS:
            en = perms.get(key, False)
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_dp_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    # VIP یا member → VIP_PERMS
    # ★ ادمین → ADMIN_PERMS
    elif role == "admin":
        import sqlite3
        from config import DATABASE_PATH
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT perm_name, enabled FROM admin_permissions WHERE chat_id=? AND user_id=? AND role='admin'", (chat_id, target_id))
            perms = {r[0]: bool(r[1]) for r in c.fetchall()}
            conn.close()
        except Exception:
            perms = {}
        keyboard.append([InlineKeyboardButton("🛡️ مدیر گروه", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in ADMIN_PERMS:
            en = perms.get(key, False)
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_ap_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    elif role in ("vip", "member"):
        perms = get_user_perms(chat_id, target_id)
        if not perms:
            perms = {k: True for k, _ in VIP_PERMS}
        keyboard.append([InlineKeyboardButton("👤 عضو ویژه / عادی", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in VIP_PERMS:
            en = perms.get(key, False)
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_vp_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    keyboard.append([InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])
    return InlineKeyboardMarkup(keyboard)


async def access_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    text = (msg.text or "").strip()
    if text != "دسترسی":
        return

    if not await can_manage_access(chat, user.id):
        await msg.reply_text("⛔ فقط سازنده ربات، ادمین های ربات، مالک گروه یا سازنده گروه می تونن دسترسی رو ببینن.")
        return

    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text(
            "روی پیام کاربر ریپلای کن و بنویس: دسترسی" + NL + NL +
            "می تونی اطلاعات و دسترسی های کاربر رو ببینی:" + NL +
            "• اگه ادمین باشه → دسترسی هاش" + NL +
            "• اگه عضو ویژه باشه → دسترسی VIP" + NL +
            "• اگه مالک/معاون باشه → دسترسی های تنظیمات"
        )
        return

    target = msg.reply_to_message.from_user
    if target.id == context.bot.id:
        return

    # نقش کاربر هدف
    target_role = get_target_role(chat.id, target.id)
    target_name = display_user(target)

    # آیا کاربری که نگاه می کنه، سازنده/سودوئه؟
    viewer_is_owner = await is_bot_owner_or_admin(user.id)

    # چک: اگه هدف مالک ربات یا ادمین ربات باشه → فقط سازنده می تونه ببینه
    if target_role in ("bot_owner", "bot_admin"):
        if not viewer_is_owner:
            await msg.reply_text("⛔ فقط سازنده ربات می تونه دسترسی سازنده یا ادمین های ربات رو ببینه.")
            return

    # آمار
    bot_admin_status = "بله" if target_role == "bot_admin" else "خیر"
    vip_status = "بله" if target_role == "vip" else "خیر"
    deputy_status = "بله" if target_role == "deputy" else "خیر"
    gowner_status = "بله" if target_role == "group_owner" else "خیر"

    header = (
        "اطلاعات کاربر:" + NL +
        "━━━━━━━━━━━━━━━━━━" + NL +
        "👤 نام: " + target_name + NL +
        "🆔 آیدی: " + str(target.id) + NL +
        "━━━━━━━━━━━━━━━━━━" + NL +
        role_emoji(target_role) + " نقش فعلی: " + role_label(target_role) + NL +
        "━━━━━━━━━━━━━━━━━━" + NL +
        "📋 وضعیت:" + NL +
        "• ادمین ربات (سودو): " + bot_admin_status + NL +
        "• عضو ویژه (VIP): " + vip_status + NL +
        "• معاون گروه: " + deputy_status + NL +
        "• مالک گروه: " + gowner_status + NL +
        "━━━━━━━━━━━━━━━━━━"
    )

    menu = build_access_menu(user.id, chat.id, target.id, target_name, target_role, is_bot_owner_user=viewer_is_owner)

    try:
        await msg.reply_text(header + NL + "دسترسی ها:", reply_markup=menu)
    except Exception as e:
        print("[ACCESS MSG ERR] " + str(e))


async def access_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    await query.answer()

    if action == "acc_noop":
        return

    if action == "acc_confirm":
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        target_id = int(parts[3]) if len(parts) > 3 else None
        d = context.bot_data.get("access_changed", {})
        print(f"[ACCESS DBG READ] looking for key=({chat_id}, {target_id}), all keys={list(d.keys())}")
        was_changed = d.pop((chat_id, target_id), False)
        print(f"[ACCESS DBG READ] was_changed={was_changed}")
        
        try:
            await query.message.delete()
        except Exception:
            pass
        
        try:
            if was_changed:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ دسترسی‌ها با موفقیت به‌روزرسانی شد."
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="ℹ️ هیچ تغییری ثبت نشد."
                )
            async def _auto_del(m):
                await asyncio.sleep(5)
                try:
                    await m.delete()
                except Exception:
                    pass
            asyncio.create_task(_auto_del(msg))
        except Exception as e:
            print("[ACCESS CONFIRM MSG ERR] " + str(e))
        return
    # toggle دسترسی معاون/مالک گروه (تنظیم کلی)
    if action.startswith("acc_dp_"):
        if len(parts) < 3:
            return
        key = action.replace("acc_dp_", "").split(":")[0]
        chat_id = int(parts[2])
        try:
            chat = await context.bot.get_chat(chat_id)
            # فقط سازنده/سودو می تونه تغییر بده
            if not await is_bot_owner_or_admin(clicker):
                await query.answer("فقط سازنده ربات می تونه تغییر بده", show_alert=True)
                return
        except Exception:
            return
        toggle_deputy_perm(chat_id, key)
        context.bot_data.setdefault("access_changed", {})
        context.bot_data["access_changed"][(chat_id, target_id)] = True
        print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")
        # ★ منو رو آپدیت کن (نه delete)
        try:
            member = await chat.get_member(target_id)
            target_name = member.user.first_name or "کاربر"
        except Exception:
            target_name = "کاربر"
        t_role = get_target_role(chat_id, target_id)
        v_owner = await is_bot_owner_or_admin(clicker)
        new_menu = build_access_menu(clicker, chat_id, target_id, target_name, t_role, v_owner)
        try:
            await query.edit_message_reply_markup(reply_markup=new_menu)
        except Exception as e:
            print("[ACCESS EDIT ERR] " + str(e))
        return

    # toggle دسترسی VIP
    if action.startswith("acc_vp_"):
        if len(parts) < 4:
            return
        key = action.replace("acc_vp_", "").split(":")[0]
        chat_id = int(parts[2])
        target_id = int(parts[3])
        try:
            chat = await context.bot.get_chat(chat_id)
            if not await can_manage_access(chat, clicker):
                await query.answer("دسترسی ندارید", show_alert=True)
                return
        except Exception:
            return
        toggle_user_perm(chat_id, target_id, key)
        context.bot_data.setdefault("access_changed", {})
        context.bot_data["access_changed"][(chat_id, target_id)] = True
        print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")
        # ★ منو رو آپدیت کن (نه delete)
        try:
            member = await chat.get_member(target_id)
            target_name = member.user.first_name or "کاربر"
        except Exception:
            target_name = "کاربر"
        t_role = get_target_role(chat_id, target_id)
        v_owner = await is_bot_owner_or_admin(clicker)
        new_menu = build_access_menu(clicker, chat_id, target_id, target_name, t_role, v_owner)
        try:
            await query.edit_message_reply_markup(reply_markup=new_menu)
        except Exception as e:
            print("[ACCESS EDIT ERR] " + str(e))
        return

    # toggle دسترسی ادمین گروه
    if action.startswith("acc_ap_"):
        if len(parts) < 4:
            return
        key = action.replace("acc_ap_", "").split(":")[0]
        chat_id = int(parts[2])
        target_id = int(parts[3])
        try:
            chat = await context.bot.get_chat(chat_id)
            if not await can_manage_access(chat, clicker):
                await query.answer("دسترسی ندارید", show_alert=True)
                return
        except Exception:
            return
        from database import get_admin_perm, set_admin_perm
        _REV_MAP = {
            "purge": "can_delete_messages",
            "ban": "can_restrict_members",
            "pin": "can_pin_messages",
            "admin_add": "can_invite_users",
            "vcall": "can_manage_video_chats",
            "group_info": "can_change_info",
        }
        _cur = get_admin_perm(chat_id, target_id, key)
        _new = 0 if _cur else 1
        set_admin_perm(chat_id, target_id, "admin", key, _new)
        if key in _REV_MAP:
            set_admin_perm(chat_id, target_id, "admin", _REV_MAP[key], _new)
        print(f"[ACC_AP] {key} = {_new}")
        context.bot_data.setdefault("access_changed", {})
        context.bot_data["access_changed"][(chat_id, target_id)] = True
        print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")
        # ★ منو رو آپدیت کن (نه delete)
        try:
            member = await chat.get_member(target_id)
            target_name = member.user.first_name or "کاربر"
        except Exception:
            target_name = "کاربر"
        t_role = get_target_role(chat_id, target_id)
        v_owner = await is_bot_owner_or_admin(clicker)
        new_menu = build_access_menu(clicker, chat_id, target_id, target_name, t_role, v_owner)
        try:
            await query.edit_message_reply_markup(reply_markup=new_menu)
        except Exception as e:
            print("[ACCESS EDIT ERR] " + str(e))
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, access_handler, block=False), group=90)
    app.add_handler(CallbackQueryHandler(access_cb_handler, pattern="^acc_"), group=91)
