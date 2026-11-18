"""
ماژول جوین اجباری (Force Join) - نسخه 3.0
- گلوبال (chat_id=0)
- چک کردن قبل از هر دستور (Middleware)
- دکمه بررسی عضویت
- دستور معاف کردن برای OWNER/SUDO
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    ApplicationHandlerStop, filters
)

NL = chr(10)
FJ_WAIT = {}


def _build_join_msg(target_name, target_link):
    text = ("🔒 برای استفاده از ربات، ابتدا باید در کانال/گروه زیر عضو شوید:" + NL + NL +
            "📢 " + (target_name or "کانال") + NL)
    if target_link:
        text += "🔗 " + target_link + NL
    text += NL + "بعد از عضویت، روی «✅ بررسی عضویت» بزنید."
    return text


async def fj_exempt_cmd(update, context):
    """معاف از جوین اجباری"""
    msg = update.effective_message
    user = update.effective_user
    if not msg or not msg.reply_to_message:
        await msg.reply_text("❌ روی پیام کاربر مورد نظر ریپلای کنید.")
        return
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo, can_exempt_fj, add_fj_exemption
        if user.id != OWNER_ID and not is_bot_owner_or_sudo(user.id):
            await msg.reply_text("❌ شما اجازه این کار را ندارید.")
            return
        if user.id != OWNER_ID and not can_exempt_fj(user.id):
            await msg.reply_text("❌ شما دسترسی «معاف کردن» را ندارید.")
            return
        target = msg.reply_to_message.from_user
        if not target:
            await msg.reply_text("❌ کاربر یافت نشد.")
            return
        add_fj_exemption(target.id, user.id)
        await msg.reply_text("✅ " + (target.first_name or "کاربر") + " از جوین اجباری معاف شد.")
    except Exception as e:
        print("[FJ EXEMPT ERR] " + str(e))
        await msg.reply_text("❌ خطا: " + str(e)[:150])


async def fj_unexempt_cmd(update, context):
    """لغو معافیت از جریمه اجباری"""
    msg = update.effective_message
    user = update.effective_user
    if not msg or not msg.reply_to_message:
        await msg.reply_text("❌ روی پیام کاربر مورد نظر ریپلای کنید.")
        return
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo, can_exempt_fj, remove_fj_exemption
        if user.id != OWNER_ID and not is_bot_owner_or_sudo(user.id):
            await msg.reply_text("❌ شما اجازه این کار را ندارید.")
            return
        if user.id != OWNER_ID and not can_exempt_fj(user.id):
            await msg.reply_text("❌ شما دسترسی «معاف کردن» را ندارید.")
            return
        target = msg.reply_to_message.from_user
        if not target:
            await msg.reply_text("❌ کاربر یافت نشد.")
            return
        remove_fj_exemption(target.id)
        await msg.reply_text("✅ معافیت " + (target.first_name or "کاربر") + " لغو شد.")
    except Exception as e:
        print("[FJ UNEXEMPT ERR] " + str(e))
        await msg.reply_text("❌ خطا: " + str(e)[:150])


async def fj_link_handler(update, context):
    """گرفتن لینک ارسالی کاربر برای تنظیم جوین اجباری"""
    user = update.effective_user
    msg = update.effective_message
    if not user or not msg or not msg.text:
        return
    if user.id not in FJ_WAIT:
        return

    # کاربر توی حالت انتظار لینکه
    link = msg.text.strip()

    # اعتبارسنجی ساده
    ok = link.startswith("https://t.me/") or link.startswith("http://t.me/") or \
         link.startswith("t.me/") or link.startswith("@") or \
         link.startswith("-100") or link.startswith("https://telegram.me/")

    if not ok:
        await msg.reply_text("❌ لینک نامعتبر! لطفاً یه لینک t.me یا آیدی بفرست.")
        return

    # ذخیره توی دیتابیس
    try:
        from database import set_setting, set_global_force_join
        saved = False
        try:
            _nm = (link.split("t.me/")[-1].split("/")[0].split("?")[0][:40] if "t.me/" in link else (link[1:][:40] if link.startswith("@") else link[:40]))
            add_global_force_join(-1, link, _nm)
            saved = True
        except Exception:
            pass
        if not saved:
            try:
                from database import add_global_force_join as _agfj
                _agfj(-1, link, "fj_group")
                set_setting(0, "fj_enabled", "1")
            except Exception as e:
                print("[FJ SAVE ERR] " + str(e))
                await msg.reply_text("❌ خطا در ذخیره لینک")
                return
    except Exception as e:
        print("[FJ IMPORT ERR] " + str(e))
        await msg.reply_text("❌ خطای دیتابیس: " + str(e))
        return

    # پاک کردن FJ_WAIT
    FJ_WAIT.pop(user.id, None)

    await msg.reply_text(
        "✅ لینک جوین اجباری ذخیره شد!" + NL + NL +
        "🔗 " + link,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت به جوین اجباری",
                callback_data="s_fj_menu:" + str(user.id) + ":0")]
        ])
    )
    raise ApplicationHandlerStop



# [MULTI-FJ-MW-START]
async def fj_middleware(update, context):
    """چک عضویت در همه FJ ها (چند لینک)"""
    if not update.effective_user:
        return
    user = update.effective_user
    if user.is_bot:
        return
    if update.effective_message and update.effective_message.text and update.effective_message.text.startswith("VCSTAT:"):
        return
    try:
        from database import is_fj_enabled
        if not is_fj_enabled():
            return
    except Exception:
        return
    try:
        from config import OWNER_ID
        if user.id == OWNER_ID:
            return
    except Exception:
        pass
    try:
        from database import is_bot_owner_or_sudo
        if is_bot_owner_or_sudo(user.id):
            return
    except Exception:
        pass
    try:
        from database import is_fj_exempt
        if is_fj_exempt(user.id):
            return
    except Exception:
        pass
    # گرفتن همه FJ ها
    try:
        from database import get_all_global_force_joins
        all_fjs = get_all_global_force_joins()
    except Exception as e:
        print("[FJ MW GET ERR] " + str(e))
        return
    if not all_fjs:
        return
    # چک عضویت در همه
    missing = []
    for fid, tid, tlink, tname in all_fjs:
        try:
            member = await context.bot.get_chat_member(tid, user.id)
            if member.status in ("left", "kicked"):
                missing.append((fid, tid, tlink, tname))
        except Exception as e:
            print("[FJ MW CHK ERR] fid=" + str(fid) + " " + str(e))
            # اگه نمی‌تونیم چک کنیم، skip می‌کنیم
    if not missing:
        return
    # ساخت پیام
    text = ("🔔 برای استفاده از ربات، باید تو این کانال/گروه‌ها عضو بشی:" + NL + NL)
    btns = []
    for fid, tid, tlink, tname in missing:
        text += "• " + (tname or str(tid)) + NL
        if tlink:
            btns.append([InlineKeyboardButton("📢 " + (tname or "عضویت")[:30], url=tlink)])
    btns.append([InlineKeyboardButton("✅ عضو شدم", callback_data="fj_check")])
    try:
        if update.effective_message:
            await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), disable_web_page_preview=True)
    except Exception as e:
        print("[FJ MW SEND ERR] " + str(e))
    raise ApplicationHandlerStop

async def fj_check_callback(update, context):
    """چک عضویت بعد از کلیک"""
    query = update.callback_query
    user = query.from_user
    try:
        from database import get_all_global_force_joins
        all_fjs = get_all_global_force_joins()
    except Exception as e:
        print("[FJ CB GET ERR] " + str(e))
        await query.answer("خطا", show_alert=True)
        return
    if not all_fjs:
        await query.answer("✅ جوین اجباری تنظیم نشده", show_alert=True)
        return
    missing = []
    for fid, tid, tlink, tname in all_fjs:
        try:
            member = await context.bot.get_chat_member(tid, user.id)
            if member.status in ("left", "kicked"):
                missing.append(tname or str(tid))
        except Exception:
            pass
    if missing:
        await query.answer("❌ هنوز تو اینا عضو نشدی: " + ", ".join(missing), show_alert=True)
        return
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.answer("✅ تایید شد! حالا می‌تونی از ربات استفاده کنی", show_alert=True)
# [MULTI-FJ-MW-END]

def register(app):
    # [FIX] handler گرفتن لینک FJ (اول همه)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, fj_link_handler),
        group=-46
    )
    """ثبت هندلرها"""
    # Middleware - group=-1 (اول از همه)
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.StatusUpdate.ALL,
            fj_middleware
        ),
        group=-1
    )

    # دکمه بررسی
    app.add_handler(
        CallbackQueryHandler(fj_check_callback, pattern="^fj_check:"),
        group=-1
    )

    # دستور معاف کردن
    app.add_handler(
        MessageHandler(filters.Regex(r"^معاف از جوین اجباری$"), fj_exempt_cmd),
        group=1
    )
    # دستور لغو معافیت
    app.add_handler(
        MessageHandler(filters.Regex(r"^لغو معافیت از جوین اجباری$"), fj_unexempt_cmd),
        group=1
    )

    print("OK module force_join loaded")
