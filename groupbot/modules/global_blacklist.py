"""ماژول بلاک‌لیست سراسری - فقط سازنده و سودوها"""
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import (
    is_global_blacklisted, add_to_global_blacklist, remove_from_global_blacklist,
    get_all_global_blacklist, log_gbl_action, is_bot_admin, get_all_bot_chats
)


async def check_blacklist_on_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اگه کاربر جدید بلاک بود، بنش کن"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.new_chat_members:
        return

    for new_member in msg.new_chat_members:
        uid = new_member.id
        if uid == OWNER_ID:
            continue
        try:
            if is_bot_admin(uid):
                continue
        except Exception:
            pass
        if is_global_blacklisted(uid, new_member.username):
            try:
                await context.bot.ban_chat_member(chat.id, uid)
                log_gbl_action(uid, chat.id, "banned_on_join", 0)
                print(f"[GBL] Banned {uid} ({new_member.username}) from {chat.id}")
            except Exception as e:
                print(f"[GBL BAN ERR] {e}")


async def gbl_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستورات /gban /gunban /glist"""
    msg = update.effective_message
    user = update.effective_user
    if not msg or not user:
        return
    try:
        if user.id != OWNER_ID and not is_bot_admin(user.id):
            return
    except Exception:
        return

    text = (msg.text or "").strip()
    parts = text.split(maxsplit=2)
    cmd = parts[0].lstrip("/").split("@")[0].lower()

    if cmd == "gban":
        if len(parts) < 2:
            await msg.reply_text("❌ استفاده: /gban <آیدی یا @یوزرنیم> [دلیل]")
            return
        target = parts[1]
        reason = parts[2] if len(parts) > 2 else ""
        target_id, target_username, target_fn = None, None, ""

        if target.startswith("@") or not target.lstrip("-").isdigit():
            target_username = target.lstrip("@").lower()
            if msg.reply_to_message and msg.reply_to_message.from_user:
                ru = msg.reply_to_message.from_user
                if ru.username and ru.username.lower() == target_username:
                    target_id = ru.id
                    target_fn = ru.first_name
            if not target_id:
                await msg.reply_text(f"❌ نتونستم @{target_username} رو پیدا کنم.\nاگه آیدی عددی داری، از /gban <id> استفاده کن.")
                return
        else:
            try:
                target_id = int(target)
            except ValueError:
                await msg.reply_text("❌ آیدی نامعتبر.")
                return

        if add_to_global_blacklist(target_id, target_username, target_fn, user.id, reason):
            await msg.reply_text(f"✅ `{target_id}` به بلاک‌لیست سراسری اضافه شد.", parse_mode="Markdown")
            try:
                chats = get_all_bot_chats()
                cnt = 0
                for cid, _ in chats:
                    try:
                        await context.bot.ban_chat_member(cid, target_id)
                        log_gbl_action(target_id, cid, "banned", user.id)
                        cnt += 1
                    except Exception:
                        pass
                if cnt:
                    await msg.reply_text(f"🚫 از {cnt} گروه بن شد.")
            except Exception as e:
                print(f"[GBL BROADCAST ERR] {e}")
        else:
            await msg.reply_text("❌ خطا در افزودن.")

    elif cmd == "gunban":
        if len(parts) < 2:
            await msg.reply_text("❌ استفاده: /gunban <آیدی عددی>")
            return
        try:
            target_id = int(parts[1])
        except ValueError:
            await msg.reply_text("❌ آیدی باید عددی باشه.")
            return
        if remove_from_global_blacklist(target_id):
            await msg.reply_text(f"✅ `{target_id}` از بلاک‌لیست حذف شد.", parse_mode="Markdown")
            try:
                chats = get_all_bot_chats()
                for cid, _ in chats:
                    try:
                        await context.bot.unban_chat_member(cid, target_id)
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            await msg.reply_text("❌ توی بلاک‌لیست نبود.")

    elif cmd == "glist":
        rows = get_all_global_blacklist()
        if not rows:
            await msg.reply_text("📋 بلاک‌لیست خالیه.")
            return
        lines = [f"📋 *بلاک‌لیست سراسری ({len(rows)} نفر):*\n"]
        for r in rows[:30]:
            uid, un, fn, ab, at, rn = r
            line = f"• `{uid}`"
            if un:
                line += f" | @{un}"
            if rn:
                line += f"\n  📝 {rn}"
            lines.append(line)
        if len(rows) > 30:
            lines.append(f"\n... و {len(rows) - 30} نفر دیگه")
        await msg.reply_text("\n".join(lines), parse_mode="Markdown")


def build_gbl_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ افزودن با آیدی", callback_data="gbl_add_id")],
        [InlineKeyboardButton("➕ افزودن با یوزرنیم", callback_data="gbl_add_un")],
        [InlineKeyboardButton("📋 نمایش لیست", callback_data="gbl_list")],
        [InlineKeyboardButton("🗑 حذف از لیست", callback_data="gbl_remove")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings")],
    ])


async def gbl_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    # جدا کردن عملگر از پارامترها
    action = data.split(":")[0] if ":" in data else data

    if action == "gbl_menu":
        rows = get_all_global_blacklist()
        text = f"🚫 *بلاک‌لیست سراسری*\n\nتعداد: {len(rows)} نفر\n\nاز دکمه‌ها استفاده کن:"
        try:
            await query.edit_message_text(text, reply_markup=build_gbl_menu(), parse_mode="Markdown")
        except Exception:
            await query.edit_message_reply_markup(reply_markup=build_gbl_menu())
        await query.answer()
        return

    if action == "gbl_list":
        rows = get_all_global_blacklist()
        if not rows:
            await query.answer("لیست خالیه!", show_alert=True)
            return
        lines = [f"📋 *بلاک‌لیست ({len(rows)} نفر):*\n"]
        for r in rows[:25]:
            uid, un, fn, ab, at, rn = r
            line = f"• `{uid}`"
            if un:
                line += f" | @{un}"
            lines.append(line)
        if len(rows) > 25:
            lines.append(f"\n... و {len(rows) - 25} نفر دیگه")
        kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data="gbl_menu")]]
        try:
            await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "gbl_add_id":
        context.user_data["gbl_waiting"] = "id"
        kb = [[InlineKeyboardButton("❌ لغو", callback_data="gbl_menu")]]
        try:
            await query.edit_message_text("🔢 آیدی عددی کاربر رو بفرست:\n\nمثال: `123456789`",
                reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "gbl_add_un":
        context.user_data["gbl_waiting"] = "username"
        kb = [[InlineKeyboardButton("❌ لغو", callback_data="gbl_menu")]]
        try:
            await query.edit_message_text("👤 یوزرنیم کاربر رو بفرست (با @):\n\nمثال: `@spammer123`",
                reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "gbl_remove":
        context.user_data["gbl_waiting"] = "remove"
        kb = [[InlineKeyboardButton("❌ لغو", callback_data="gbl_menu")]]
        try:
            await query.edit_message_text("🗑 آیدی عددی کاربری که می‌خوای از بلاک‌لیست حذف بشه رو بفرست:",
                reply_markup=InlineKeyboardMarkup(kb))
        except Exception:
            pass
        await query.answer()
        return

    await query.answer()


async def gbl_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if not msg or not user or not msg.text:
        return
    if user.id != OWNER_ID:
        return
    waiting = context.user_data.get("gbl_waiting")
    if not waiting:
        return
    text = msg.text.strip()

    if waiting == "id":
        try:
            tid = int(text)
        except ValueError:
            await msg.reply_text("❌ آیدی باید عددی باشه. دوباره بفرست یا از پنل لغو کن:")
            raise ApplicationHandlerStop
        if add_to_global_blacklist(tid, "", "", user.id, "افزودن از پنل"):
            await msg.reply_text(f"✅ `{tid}` به بلاک‌لیست اضافه شد.", parse_mode="Markdown")
        else:
            await msg.reply_text("❌ خطا.")
        context.user_data.pop("gbl_waiting", None)
        raise ApplicationHandlerStop

    if waiting == "username":
        uname = text.lstrip("@").lower()
        if not uname:
            await msg.reply_text("❌ یوزرنیم نامعتبره.")
            raise ApplicationHandlerStop
        if add_to_global_blacklist(0, uname, "", user.id, "افزودن از پنل"):
            await msg.reply_text(f"✅ @{uname} به بلاک‌لیست اضافه شد.", parse_mode="Markdown")
        else:
            await msg.reply_text("❌ خطا.")
        context.user_data.pop("gbl_waiting", None)
        raise ApplicationHandlerStop

    if waiting == "remove":
        try:
            tid = int(text)
        except ValueError:
            await msg.reply_text("❌ آیدی باید عددی باشه.")
            raise ApplicationHandlerStop
        if remove_from_global_blacklist(tid):
            await msg.reply_text(f"✅ `{tid}` از بلاک‌لیست حذف شد.", parse_mode="Markdown")
        else:
            await msg.reply_text("❌ توی بلاک‌لیست نبود.")
        context.user_data.pop("gbl_waiting", None)
        raise ApplicationHandlerStop


def register(app):
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_blacklist_on_join),
        group=-200
    )
    app.add_handler(CommandHandler(["gban", "gunban", "glist"], gbl_cmd), group=-2)
    app.add_handler(CallbackQueryHandler(gbl_cb_handler, pattern=r"^gbl_"), group=-2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gbl_text_handler), group=-4)
    print("OK module global_blacklist loaded")
