"""پنل مدیریت AI - تنظیم کلیدها و مدل‌ها از خود ربات"""
import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import get_setting, set_setting




async def _delayed_delete(context, chat_id, message_id, delay=5):
    """حذف پیام بعد از N ثانیه"""
    import asyncio
    try:
        await asyncio.sleep(delay)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print("[AUTO DEL ERR]", str(e))


def _mask_key(key):
    if not key:
        return "تنظیم نشده"
    if len(key) < 12:
        return "تنظیم شده"
    return key[:8] + "..." + key[-4:]


def build_ai_panel():
    hf_key = get_setting(0, "ai_hf_key", "")
    or_key = get_setting(0, "ai_openrouter_key", "")
    global_en = get_setting(0, "ai_global_enabled", "1") == "1"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 HuggingFace: " + _mask_key(hf_key), callback_data="ai_set_hf")],
        [InlineKeyboardButton("🔑 OpenRouter: " + _mask_key(or_key), callback_data="ai_set_or")],
        [InlineKeyboardButton("🌐 فعال سراسری: " + ("✅" if global_en else "❌"), callback_data="ai_toggle_global")],
        [InlineKeyboardButton("🧪 تست HuggingFace", callback_data="ai_test_hf")],
        [InlineKeyboardButton("🧪 تست OpenRouter", callback_data="ai_test_or")],
        [InlineKeyboardButton("📋 مدل‌های HuggingFace", callback_data="ai_hf_models")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sys_menu:owner")],
    ])


def build_hf_models_menu():
    try:
        models = json.loads(get_setting(0, "ai_hf_models", "[]"))
    except Exception:
        models = []
    if not models:
        models = ["meta-llama/Llama-3.3-70B-Instruct",
                  "Qwen/Qwen2.5-72B-Instruct",
                  "meta-llama/Llama-3.1-8B-Instruct"]
        set_setting(0, "ai_hf_models", json.dumps(models))

    rows = []
    for i, m in enumerate(models):
        short = m.split("/")[-1][:25]
        rows.append([InlineKeyboardButton("❌ " + short, callback_data="ai_hf_rm:" + str(i))])
    rows.append([InlineKeyboardButton("➕ افزودن مدل", callback_data="ai_hf_add")])
    rows.append([InlineKeyboardButton("🔄 بازنشانی", callback_data="ai_hf_reset")])
    rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ai_panel")])
    return InlineKeyboardMarkup(rows)


async def ai_mgmt_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    data = query.data

    if data == "ai_panel":
        try:
            await query.edit_message_text("🤖 *مدیریت AI*\n\nاز دکمه‌ها استفاده کن:",
                                          reply_markup=build_ai_panel(),
                                          parse_mode="Markdown")
        except Exception as e:
            print("[AI PANEL ERR]", str(e))
        await query.answer()
        return

    if data == "ai_toggle_global":
        cur = get_setting(0, "ai_global_enabled", "1")
        new = "0" if cur == "1" else "1"
        set_setting(0, "ai_global_enabled", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_ai_panel())
        except Exception:
            pass
        await query.answer("✅ تغییر کرد")
        return

    if data == "ai_set_hf":
        context.user_data["ai_waiting"] = "hf"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو", callback_data="ai_panel")]])
        try:
            await query.edit_message_text("🔑 کلید HuggingFace رو بفرست:\n\nمثال: `hf_abcdef...`\n\n(پیام کلید خودکار حذف می‌شه)",
                                          reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if data == "ai_set_or":
        context.user_data["ai_waiting"] = "or"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو", callback_data="ai_panel")]])
        try:
            await query.edit_message_text("🔑 کلید OpenRouter رو بفرست:\n\nمثال: `sk-or-v1-...`",
                                          reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if data == "ai_test_hf":
        await query.answer("🧪 در حال تست...")
        try:
            await query.edit_message_text("🧪 *در حال تست HuggingFace...*")
        except Exception:
            pass
        await _run_hf_test(query, context, user.id)
        return

    if data == "ai_test_or":
        await query.answer("🧪 در حال تست...")
        try:
            await query.edit_message_text("🧪 *در حال تست OpenRouter...*")
        except Exception:
            pass
        await _run_or_test(query, context, user.id)
        return

    if data == "ai_hf_models":
        try:
            await query.edit_message_text("📋 *مدل‌های HuggingFace*\n\nبرای حذف، روی مدل بزن:",
                                          reply_markup=build_hf_models_menu(),
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if data.startswith("ai_hf_rm:"):
        try:
            i = int(data.split(":")[1])
            models = json.loads(get_setting(0, "ai_hf_models", "[]"))
            if 0 <= i < len(models):
                models.pop(i)
                set_setting(0, "ai_hf_models", json.dumps(models))
                try:
                    await query.edit_message_reply_markup(reply_markup=build_hf_models_menu())
                except Exception:
                    pass
                await query.answer("✅ حذف شد")
        except Exception as e:
            print("[HF RM ERR]", str(e))
        return

    if data == "ai_hf_add":
        context.user_data["ai_waiting"] = "hf_model"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو", callback_data="ai_hf_models")]])
        try:
            await query.edit_message_text("➕ اسم مدل HF رو بفرست:\n\nمثال: `Qwen/Qwen2.5-72B-Instruct`",
                                          reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if data == "ai_hf_reset":
        default = ["meta-llama/Llama-3.3-70B-Instruct",
                   "Qwen/Qwen2.5-72B-Instruct",
                   "meta-llama/Llama-3.1-8B-Instruct"]
        set_setting(0, "ai_hf_models", json.dumps(default))
        try:
            await query.edit_message_reply_markup(reply_markup=build_hf_models_menu())
        except Exception:
            pass
        await query.answer("✅ بازنشانی شد")
        return

    await query.answer()


async def _run_hf_test(query, context, user_id):
    key = get_setting(0, "ai_hf_key", "")
    if not key:
        try:
            p = os.path.expanduser("~/.hf_key")
            if os.path.exists(p):
                with open(p) as f:
                    key = f.read().strip()
        except Exception:
            pass

    if not key:
        result = "❌ *کلید HuggingFace تنظیم نشده!*"
    else:
        try:
            models = json.loads(get_setting(0, "ai_hf_models", "[]"))
            if not models:
                models = ["meta-llama/Llama-3.3-70B-Instruct"]
            model = models[0]
            url = "https://router.huggingface.co/v1/chat/completions"
            headers = {
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "سلام"}],
                "max_tokens": 10,
            }
            r = requests.post(url, headers=headers, json=payload, timeout=25)
            if r.status_code == 200:
                d = r.json()
                reply = d.get("choices", [{}])[0].get("message", {}).get("content", "")
                result = "✅ *HuggingFace کار می‌کنه!*\n\nمدل: `" + model + "`\n\nجواب تست: `" + (reply[:50] if reply else "خالی") + "`"
            else:
                err = r.text[:250]
                result = "❌ *خطا در HuggingFace*\n\nکد: `" + str(r.status_code) + "`\n\n`" + err + "`"
        except Exception as e:
            result = "❌ *خطای غیرمنتظره*\n\n`" + str(e)[:200] + "`"

    import asyncio
    sent_msg = None
    try:
        await query.edit_message_text(result, reply_markup=build_ai_panel(), parse_mode="Markdown")
        # ذخیره message_id برای حذف
        try:
            sent_msg = query.message
        except Exception:
            pass
    except Exception as e1:
        print("[HF TEST EDIT ERR]", str(e1))
        try:
            sent_msg = await context.bot.send_message(chat_id=user_id, text=result, parse_mode="Markdown")
        except Exception as e2:
            print("[HF TEST SEND ERR]", str(e2))
            try:
                sent_msg = await context.bot.send_message(chat_id=user_id, text="نتیجه تست: " + result)
            except Exception:
                pass

    # بعد از 5 ثانیه پیام نتیجه رو حذف کن
    if sent_msg:
        asyncio.create_task(_delayed_delete(context, sent_msg.chat_id, sent_msg.message_id, 5))


async def _run_or_test(query, context, user_id):
    key = get_setting(0, "ai_openrouter_key", "")
    if not key:
        try:
            p = os.path.expanduser("~/.openrouter_key")
            if os.path.exists(p):
                with open(p) as f:
                    key = f.read().strip()
        except Exception:
            pass

    if not key:
        result = "❌ *کلید OpenRouter تنظیم نشده!*"
    else:
        try:
            model = get_setting(0, "ai_model", "meta-llama/llama-3.3-70b-instruct")
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "سلام"}],
                "max_tokens": 10,
            }
            r = requests.post(url, headers=headers, json=payload, timeout=25)
            if r.status_code == 200:
                d = r.json()
                reply = d.get("choices", [{}])[0].get("message", {}).get("content", "")
                result = "✅ *OpenRouter کار می‌کنه!*\n\nمدل: `" + model + "`\n\nجواب: `" + (reply[:50] if reply else "خالی") + "`"
            else:
                err = r.text[:250]
                result = "❌ *خطا در OpenRouter*\n\nکد: `" + str(r.status_code) + "`\n\n`" + err + "`"
        except Exception as e:
            result = "❌ *خطای غیرمنتظره*\n\n`" + str(e)[:200] + "`"

    import asyncio
    sent_msg = None
    try:
        await query.edit_message_text(result, reply_markup=build_ai_panel(), parse_mode="Markdown")
        try:
            sent_msg = query.message
        except Exception:
            pass
    except Exception as e1:
        print("[OR TEST EDIT ERR]", str(e1))
        try:
            sent_msg = await context.bot.send_message(chat_id=user_id, text=result, parse_mode="Markdown")
        except Exception:
            try:
                sent_msg = await context.bot.send_message(chat_id=user_id, text="نتیجه: " + result)
            except Exception:
                pass

    if sent_msg:
        asyncio.create_task(_delayed_delete(context, sent_msg.chat_id, sent_msg.message_id, 5))


async def ai_mgmt_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if not msg or not user or user.id != OWNER_ID:
        return
    waiting = context.user_data.get("ai_waiting")
    if not waiting:
        return
    text = (msg.text or "").strip()

    try:
        await msg.delete()
    except Exception:
        pass

    if waiting == "hf":
        set_setting(0, "ai_hf_key", text)
        context.user_data.pop("ai_waiting", None)
        try:
            await context.bot.send_message(chat_id=user.id, text="✅ کلید HuggingFace ذخیره شد.")
        except Exception:
            pass
        raise ApplicationHandlerStop

    if waiting == "or":
        set_setting(0, "ai_openrouter_key", text)
        context.user_data.pop("ai_waiting", None)
        try:
            await context.bot.send_message(chat_id=user.id, text="✅ کلید OpenRouter ذخیره شد.")
        except Exception:
            pass
        raise ApplicationHandlerStop

    if waiting == "hf_model":
        try:
            models = json.loads(get_setting(0, "ai_hf_models", "[]"))
            if text not in models:
                models.append(text)
                set_setting(0, "ai_hf_models", json.dumps(models))
            try:
                await context.bot.send_message(chat_id=user.id, text="✅ مدل اضافه شد:\n" + text)
            except Exception:
                pass
        except Exception as e:
            print("[HF ADD ERR]", str(e))
        context.user_data.pop("ai_waiting", None)
        raise ApplicationHandlerStop


def register(app):
    app.add_handler(
        CallbackQueryHandler(
            ai_mgmt_cb,
            pattern=r"^ai_(panel|toggle_global|set_hf|set_or|test_hf|test_or|hf_models|hf_rm|hf_add|hf_reset)"
        ),
        group=-42
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, ai_mgmt_text),
        group=-42
    )
    print("OK module ai_management loaded")
