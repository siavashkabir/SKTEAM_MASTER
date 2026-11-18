"""AI Chat - پاسخ هوشمند با OpenRouter"""
import os
import re
import asyncio
import datetime
import requests
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from config import OWNER_ID
from database import (
    get_setting,
    get_ai_setting, set_ai_setting, get_ai_usage_today, log_ai_usage,
    is_bot_admin, is_group_owner, is_vip, get_chat_panel_delete, get_chat_ai_delete
)

DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
DEFAULT_LIMIT = 1000


def _load_api_key():
    """خوندن OpenRouter Key - اول از دیتابیس، بعد فایل"""
    try:
        v = get_setting(0, "ai_openrouter_key", "")
        if v:
            return v
    except Exception:
        pass
    try:
        key_path = os.path.expanduser("~/.openrouter_key")
        with open(key_path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""


# ==================== شخصیت‌ها ====================
PERSONALITIES = {
    "persian": {
        "name": "طنز",
        "emoji": "😄",
        "prompt": """تو یه ربات باحال و طنز توی گروه تلگرام هستی. فقط فارسی جواب بده. کوتاه، بامزه، شیطون.
بعضی وقتا از فحش‌های ملایم مثل «خنگ، خرفت، بیشعور، نادان، خرف، دیوونه» استفاده کن ولی فحش رکیک جنسی نگو.
جواب‌هات کوتاه باشه (حداکثر ۲ جمله). ایموجی‌های بامزه بذار."""
    },
    "formal": {
        "name": "مؤدب",
        "emoji": "🙂",
        "prompt": """تو یه ربات مؤدب و مرتب توی گروه تلگرام هستی. فقط فارسی جواب بده.
کوتاه، محترمانه، بدون هیچ فحشی. جواب‌هات حداکثر ۲ جمله باشه. ایموجی کم استفاده کن."""
    },
    "funny": {
        "name": "بامزه",
        "emoji": "🤣",
        "prompt": """تو یه ربات شاد و بامزه توی گروه تلگرام هستی. فقط فارسی جواب بده.
طنز کودکانه، جک‌های ساده، بازی با کلمات. بدون فحش. کوتاه و شیرین. ایموجی زیاد بذار."""
    },
    "cool": {
        "name": "خفن",
        "emoji": "😎",
        "prompt": """تو یه ربات خفن و باکلاس توی گروه تلگرام هستی. فقط فارسی جواب بده.
کمی مغرور، باکلاس، کوتاه و کوبنده. فحش‌های ملایم مجاز. حداکثر ۲ جمله. ایموجی‌های 😎🔥💪."""
    },
    "rude": {
        "name": "خیلی خیلی خفن",
        "emoji": "😈",
        "prompt": """تو یه ربات خیلی خیلی خفن و رک توی گروه تلگرام هستی. فقط فارسی جواب بده.
اصلاً مؤدب نباش. اگه کسی بهت فحش داد، با فحش ملایم جوابش بده. اگه مسخره‌ات کرد، تیکه بنداز.
از کلماتی مثل «خنگ، خرفت، بیشعور، نادان، خرف، دیوونه، عقل کل، کله‌پوک، بی‌مخ، گاگول، هالو، احمق، نفهم» راحت استفاده کن.
انرژی داشته باش، کوبنده جواب بده، شوخی تند بکن. حداکثر ۲ جمله. ایموجی‌های 😏😈🤣🔥 بذار.
هرگز فحش جنسی، توهین به مادر/خواهر/ننه و کلمات مستهجن نگو."""
    },
}

# فحش‌های رکیک که AI هرگز نباید بگه
FORBIDDEN_FOR_AI = [
    "کیر", "کون", "کص", "گایید", "گای", "خایه",
    "جنده", "حرومزاده", "زناکار", "لاشی", "لاطی",
    "مادرجنده", "خواهرجنده", "ننه‌جنده", "عمه‌جنده",
    "کیرخور", "کونکش", "کسکش", "کصکش",
]


def _has_forbidden(text):
    """چک میکنه متن فحش رکیک داره"""
    if not text:
        return False
    t = text.replace("\u200c", "").replace("\u200f", "").lower()
    for w in FORBIDDEN_FOR_AI:
        if w in t:
            return True
    return False


def _should_reply(msg, chat, user, context):
    """چک میکنه آیا ربات باید جواب بده"""
    text = msg.text or ""
    if not text or len(text) < 2:
        return False

    trigger = get_ai_setting(chat.id, "ai_trigger", "mention") or "mention"

    is_mentioned = False
    try:
        from config import BOT_USERNAME
        if BOT_USERNAME:
            un = BOT_USERNAME.lstrip("@").lower()
            if ("@" + un) in text.lower():
                is_mentioned = True
    except Exception:
        pass

    is_reply = False
    if msg.reply_to_message and msg.reply_to_message.from_user:
        if msg.reply_to_message.from_user.id == context.bot.id:
            is_reply = True

    has_keyword = any(
        text.lower().strip().startswith(k) or text.lower().strip() == k
        for k in ["ربات", "اسکای", "sky", "bot"]
    )

    if trigger == "mention":
        return is_mentioned or is_reply or has_keyword
    elif trigger == "30percent":
        import random
        return is_mentioned or is_reply or has_keyword or random.random() < 0.3
    elif trigger == "50percent":
        import random
        return is_mentioned or is_reply or has_keyword or random.random() < 0.5
    elif trigger == "always":
        return True
    return is_mentioned or is_reply or has_keyword


def _ask_openrouter(prompt, personality, adult_mode=False, history=None):
    """درخواست به OpenRouter (sync - توی executor اجرا میشه)"""
    api_key = _load_api_key()
    if not api_key:
        return None, "no_api_key"

    model = get_setting(0, "ai_model", DEFAULT_MODEL) or DEFAULT_MODEL
    max_tokens = int(get_setting(0, "ai_max_tokens", "2000") or "2000")

    p_data = PERSONALITIES.get(personality, PERSONALITIES["persian"])
    system_prompt = p_data["prompt"]
    if adult_mode:
        system_prompt += "\nمی‌تونی شوخی‌های بزرگسالانه بکنی ولی فحش رکیک جنسی نده."

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.9,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/sk_team_mediaplayerbot",
        "X-Title": "SK Team GroupBot",
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if r.status_code == 200:
            try:
                data = r.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if reply is None:
                    return None, "empty_response"
                reply = reply.strip()
                if not reply:
                    return None, "empty_response"
                return reply, None
            except Exception as e:
                return None, "parse_error:" + str(e)
        else:
            try:
                err = r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
            except Exception:
                err = f"HTTP {r.status_code}: {r.text[:200]}"
            return None, err
    except Exception as e:
        return None, str(e)




def _load_hf_key():
    """خوندن HF Key - اول از دیتابیس، بعد فایل"""
    try:
        v = get_setting(0, "ai_hf_key", "")
        if v:
            return v
    except Exception:
        pass
    try:
        with open(os.path.expanduser("~/.hf_key"), "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def _ask_huggingface(messages, max_tokens):
    """درخواست به Hugging Face (sync)"""
    api_key = _load_hf_key()
    if not api_key:
        return None, "no_hf_key"

    import json as _json
    models_str = get_setting(0, "ai_hf_models", "[]")
    try:
        models = _json.loads(models_str)
    except Exception:
        models = ["meta-llama/Llama-3.3-70B-Instruct"]

    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err = None
    for model in models:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.9,
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content and content.strip():
                    print(f"[HF] Success: {model}")
                    return content.strip(), None
                else:
                    last_err = f"{model}: empty"
            else:
                last_err = f"{model}: HTTP {r.status_code}"
                print(f"[HF] {last_err}")
        except Exception as e:
            last_err = f"{model}: {str(e)[:80]}"
            print(f"[HF] {last_err}")

    return None, f"all_hf_failed: {last_err}"


async def ask_ai(prompt, personality, adult_mode=False, history=None):
    """نسخه async - اول HF، بعد OpenRouter (fallback)"""
    loop = asyncio.get_event_loop()

    # ساخت messages
    p_data = PERSONALITIES.get(personality, PERSONALITIES["persian"])
    system_prompt = p_data["prompt"]
    if adult_mode:
        system_prompt += "\nمی‌تونی شوخی‌های بزرگسالانه بکنی ولی فحش رکیک جنسی نده."

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": prompt})

    max_tokens = int(get_setting(0, "ai_max_tokens", "2000") or "2000")

    # ۱. اول Hugging Face (رایگان)
    hf_enabled = get_setting(0, "ai_hf_enabled", "1") == "1"
    if hf_enabled:
        reply, err = await loop.run_in_executor(
            None, lambda: _ask_huggingface(messages, max_tokens)
        )
        if reply and not err:
            return reply, None
        print(f"[AI] HF failed: {err}, trying OpenRouter...")

    # ۲. اگه HF خطا داد، برو سراغ OpenRouter
    reply, err = await loop.run_in_executor(
        None, lambda: _ask_openrouter(prompt, personality, adult_mode, history)
    )
    return reply, err


async def ai_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر اصلی AI"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if user.is_bot:
        return

    # سراسری فعاله؟
    if get_setting(0, "ai_global_enabled", "1") != "1":
        return

    # برای این گروه فعاله؟
    if get_ai_setting(chat.id, "ai_enabled", "0") != "1":
        return

    # محدودیت روزانه
    limit = int(get_setting(0, "ai_daily_limit", str(DEFAULT_LIMIT)) or str(DEFAULT_LIMIT))
    if get_ai_usage_today() >= limit:
        return

    # باید جواب بده؟
    if not _should_reply(msg, chat, user, context):
        return

    personality = get_ai_setting(chat.id, "ai_personality", "persian") or "persian"
    adult_mode = get_ai_setting(chat.id, "ai_adult", "0") == "1"

    # چک adult mode سراسری
    if get_setting(0, "ai_global_adult", "1") != "1":
        adult_mode = False

    # نشانگر تایپ
    thinking = None
    try:
        thinking = await msg.reply_text("💭 ...")
    except Exception:
        pass

    try:
        reply, err = await ask_ai(msg.text, personality, adult_mode)
    except Exception as e:
        print("[AI ERR]", str(e))
        reply, err = None, str(e)

    if thinking:
        try:
            await thinking.delete()
        except Exception:
            pass

    if err:
        print(f"[AI ERROR] {err}")
        return
    if not reply:
        return
    try:
        reply = reply.strip()
    except Exception:
        return

    # فیلتر فحش رکیک
    if _has_forbidden(reply):
        print("[AI] Blocked reply with forbidden words")
        return

    if len(reply) > 1000:
        reply = reply[:1000] + "..."

    try:
        sent = await msg.reply_text(reply)
        log_ai_usage(chat.id, user.id)

        # حذف خودکار (از تنظیم مخصوص AI)
        try:
            delay = get_chat_ai_delete(chat.id)
            if delay > 0:
                async def _del():
                    try:
                        await asyncio.sleep(delay)
                        await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
                    except Exception:
                        pass
                asyncio.create_task(_del())
        except Exception:
            pass
    except Exception as e:
        print("[AI REPLY ERR]", str(e))


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, ai_trigger),
        group=-25
    )
    print("OK module ai_chat loaded (openrouter)")
