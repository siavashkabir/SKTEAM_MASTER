import os
import subprocess
import requests
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import SIGHTENGINE_USER, SIGHTENGINE_SECRET, OWNER_ID
from database import (
    get_setting, set_setting, add_warn,
    get_nsfw_sub, set_nsfw_sub, is_nsfw_sub_activated, get_nsfw_remaining,
    is_bot_admin
)

NL = chr(10)
API_URL = "https://api.sightengine.com/1.0/check.json"
MAX_WARNS = 4
NSFW_DATE_FMT = "%Y-%m-%d %H:%M"

SENS_LABELS = {"low": "کم", "medium": "متوسط", "high": "زیاد"}
SENS_THRESHOLD = {"low": 0.85, "medium": 0.7, "high": 0.5}


def get_sensitivity(chat_id):
    return get_setting(chat_id, "nsfw_sensitivity", "medium")


def get_threshold(chat_id):
    return SENS_THRESHOLD.get(get_sensitivity(chat_id), 0.7)


def is_group_toggle_on(chat_id):
    """آیا گروه تیک NSFW رو زده"""
    return get_setting(chat_id, "nsfw_enabled", "1") == "1"


def set_group_toggle(chat_id, enabled):
    set_setting(chat_id, "nsfw_enabled", "1" if enabled else "0")


def is_enabled(chat_id):
    """NSFW باید هم اشتراک فعال داشته باشه هم گروه روشن کرده باشه"""
    if not is_nsfw_sub_activated(chat_id):
        return False
    return is_group_toggle_on(chat_id)


# ============================================
# منوی اشتراک NSFW - فقط برای سازنده ربات و سودو
# ============================================

def build_nsfw_sub_menu(uid, chat_id):
    sub = get_nsfw_sub(chat_id)
    active = is_nsfw_sub_activated(chat_id)
    remaining = get_nsfw_remaining(chat_id)

    if not sub["expire_date"]:
        status = "فعال نیست"
        exp_line = "تاریخ انقضا: ---"
    else:
        if active:
            status = "✅ فعال"
            exp_line = "تاریخ انقضا: " + str(sub["expire_date"]) + NL + "باقی مانده: " + str(remaining) + " روز"
        else:
            status = "❌ منقضی شده"
            exp_line = "تاریخ: " + str(sub["expire_date"])

    enabled_mark = "[ON]" if sub["enabled"] else "[OFF]"

    keyboard = [
        [InlineKeyboardButton("اشتراک: " + status, callback_data="nsub_noop:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton(exp_line.replace(NL, " | "), callback_data="nsub_noop:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton(enabled_mark + " وضعیت اشتراک", callback_data="nsub_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("تمدید 30 روزه", callback_data="nsub_30:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("تمدید 60 روزه", callback_data="nsub_60:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("تمدید 90 روزه", callback_data="nsub_90:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("تمدید 180 روزه (6 ماه)", callback_data="nsub_180:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("تمدید 365 روزه (1 سال)", callback_data="nsub_365:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("غیرفعال کردن", callback_data="nsub_off:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("بازگشت", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_nsfw_menu(uid, chat_id):
    """منوی NSFW برای گروه (مالک گروه / معاون)"""
    active = is_nsfw_sub_activated(chat_id)
    remaining = get_nsfw_remaining(chat_id)
    enabled = is_group_toggle_on(chat_id)

    if active:
        sub_status = "✅ فعال"
        sub_info = "باقی مانده: " + str(remaining) + " روز"
    else:
        sub_status = "❌ غیرفعال"
        sub_info = "برای فعال سازی با پشتیبانی تماس بگیرید"

    sens = get_sensitivity(chat_id)
    sens_label = SENS_LABELS.get(sens, "متوسط")
    status = "روشن" if enabled else "خاموش"
    status_emoji = "[ON]" if enabled else "[OFF]"

    def mark(key):
        return "(x) " + SENS_LABELS[key] if sens == key else SENS_LABELS[key]

    keyboard = [
        [InlineKeyboardButton("اشتراک NSFW: " + sub_status, callback_data="nsfw_noop:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton(sub_info, callback_data="nsfw_noop:" + str(uid) + ":" + str(chat_id))],
    ]
    if active:
        keyboard.append([InlineKeyboardButton(status_emoji + " وضعیت فیلتر: " + status, callback_data="nsfw_toggle:" + str(uid) + ":" + str(chat_id))])
        keyboard.append([InlineKeyboardButton("حساسیت فعلی: " + sens_label, callback_data="nsfw_noop:" + str(uid) + ":" + str(chat_id))])
        keyboard.append([
            InlineKeyboardButton(mark("low"), callback_data="nsfw_sens_low:" + str(uid) + ":" + str(chat_id)),
            InlineKeyboardButton(mark("medium"), callback_data="nsfw_sens_medium:" + str(uid) + ":" + str(chat_id)),
            InlineKeyboardButton(mark("high"), callback_data="nsfw_sens_high:" + str(uid) + ":" + str(chat_id)),
        ])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="menu_settings:" + str(uid))])
    # دکمه ورود به تنظیمات پیشرفته
    keyboard.append([InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data="nsfw_adv:" + str(uid) + ":" + str(chat_id))])
    keyboard.append([InlineKeyboardButton("بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)


def convert_to_jpg(input_path, output_path):
    """تبدیل هر فرمتی به JPG (با پشتیبانی webm/webp/tgs)"""
    try:
        ext = os.path.splitext(input_path)[1].lower()
        if ext == ".tgs":
            # .tgs = Lottie (JSON فشرده) — ffmpeg نمی‌تونه
            print("[CONV] .tgs skip (Lottie format)")
            return False
        
        # تلاش ۱: عادی
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vframes", "1", "-q:v", "2", "-f", "image2", output_path]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        
        # تلاش ۲: برای webm / mp4 / animated
        cmd2 = ["ffmpeg", "-y", "-i", input_path, "-frames:v", "1", "-update", "1", "-q:v", "2", output_path]
        result = subprocess.run(cmd2, capture_output=True, timeout=30)
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        
        # تلاش ۳: webp animated
        cmd3 = ["ffmpeg", "-y", "-i", input_path, "-vf", "select=eq(n\\,0)", "-vframes", "1", output_path]
        result = subprocess.run(cmd3, capture_output=True, timeout=30)
        return result.returncode == 0 and os.path.exists(output_path)
    except Exception as e:
        print("[CONV ERR] " + str(e))
        return False


async def mute_user(chat, user_id):
    try:
        await chat.restrict_member(user_id=user_id, permissions=ChatPermissions(can_send_messages=False))
        return True
    except Exception as e:
        print("[MUTE ERR] " + str(e))
        return False


def build_nsfw_advanced_menu(uid, chat_id):
    """منوی پیشرفته تنظیمات برخورد NSFW"""
    warn_limit = get_setting(chat_id, "nsfw_warn_limit", "4") or "4"
    action = get_setting(chat_id, "nsfw_action", "mute") or "mute"
    duration = get_setting(chat_id, "nsfw_mute_duration", "0") or "0"
    
    limit_labels = {"3": "3", "4": "4", "5": "5", "6": "6"}
    action_labels = {"mute": "🔇 سکوت", "kick": "👢 کیک", "ban": "🚫 بن"}
    dur_labels = {"0": "دائمی", "1h": "۱ ساعت", "6h": "۶ ساعت", "24h": "۲۴ ساعت", "168h": "۱ هفته"}
    
    keyboard = []
    keyboard.append([InlineKeyboardButton("⚙️ تنظیمات NSFW پیشرفته", callback_data="nsfw_noop")])
    keyboard.append([InlineKeyboardButton("───────────────", callback_data="nsfw_noop")])
    
    keyboard.append([InlineKeyboardButton("🔔 تعداد اخطار قبل از برخورد: " + limit_labels.get(warn_limit, warn_limit), callback_data="nsfw_noop")])
    row = []
    for k in ["3", "4", "5", "6"]:
        mark = "✅" if warn_limit == k else "▫️"
        row.append(InlineKeyboardButton(mark + " " + k, callback_data="nsfw_limit_" + k + ":" + str(uid) + ":" + str(chat_id)))
    keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⚔️ نوع برخورد: " + action_labels.get(action, action), callback_data="nsfw_noop")])
    row = []
    for k in ["mute", "kick", "ban"]:
        mark = "✅" if action == k else "▫️"
        row.append(InlineKeyboardButton(mark + " " + action_labels[k], callback_data="nsfw_action_" + k + ":" + str(uid) + ":" + str(chat_id)))
    keyboard.append(row)
    
    if action == "mute":
        keyboard.append([InlineKeyboardButton("⏱️ مدت سکوت: " + dur_labels.get(duration, duration), callback_data="nsfw_noop")])
        row = []
        for k in ["0", "1h", "6h", "24h", "168h"]:
            mark = "✅" if duration == k else "▫️"
            row.append(InlineKeyboardButton(mark + " " + dur_labels[k], callback_data="nsfw_dur_" + k + ":" + str(uid) + ":" + str(chat_id)))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="nsfw_menu:" + str(uid) + ":" + str(chat_id))])
    return InlineKeyboardMarkup(keyboard)


async def check_nsfw(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    try:
        from modules.nsfw import is_group_toggle_on, is_nsfw_sub_activated
    except Exception:
        pass
    en = is_enabled(chat.id)
    from modules.nsfw import is_group_toggle_on, is_nsfw_sub_activated, is_enabled as _ie
    _dbg_chat_id = chat.id
    _ie_result = _ie(_dbg_chat_id)
    if not _ie_result:
        return
    
    # اگه Owner خودش → هیچ
    if msg.from_user and msg.from_user.id == OWNER_ID:
        return
    
    has_media = msg.photo or msg.animation or msg.video or msg.sticker or msg.document
    if not has_media:
        return
    
    if msg.document:
        mime = msg.document.mime_type or ""
        if not (mime.startswith("image/") or mime.startswith("video/")):
            return
    
    file_id = None
    if msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.animation:
        file_id = msg.animation.file_id
    elif msg.video:
        file_id = msg.video.file_id
    elif msg.sticker:
        file_id = msg.sticker.file_id
    elif msg.document:
        file_id = msg.document.file_id
    
    if not file_id:
        return
    
    threshold = get_threshold(chat.id)
    temp_input = None
    temp_jpg = None
    
    try:
        file = await context.bot.get_file(file_id)
        ext = os.path.splitext(file.file_path or "")[1] or ".bin"
        os.makedirs("downloads", exist_ok=True)
        temp_input = "downloads/nsfw_in_" + str(file_id) + ext
        temp_jpg = "downloads/nsfw_out_" + str(file_id) + ".jpg"
        await file.download_to_drive(custom_path=temp_input)
        
        ext_low = ext.lower()
        if ext_low in (".jpg", ".jpeg", ".png"):
            temp_jpg = temp_input
        else:
            if not convert_to_jpg(temp_input, temp_jpg):
                return
        
        print(f"[NSFW-FLOW] file_id={file_id[:20]}, ext={ext}, temp_jpg={temp_jpg}")
        with open(temp_jpg, "rb") as f:
            files = {"media": f}
            data = {"models": "nudity-2.1", "api_user": SIGHTENGINE_USER, "api_secret": SIGHTENGINE_SECRET}
            response = requests.post(API_URL, files=files, data=data, timeout=30)
        print(f"[NSFW-FLOW] API response: status={response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                nudity = result.get("nudity", {})
                sa = nudity.get("sexual_activity", 0)
                sd = nudity.get("sexual_display", 0)
                er = nudity.get("erotica", 0)
                print("[NSFW] act=" + str(sa) + " disp=" + str(sd) + " ero=" + str(er) + " thr=" + str(threshold))
                
                if sa >= threshold or sd >= threshold or er >= threshold:
                    print(f"[NSFW-DETECT] BAD content! sa={sa} sd={sd} er={er} thr={threshold}")
                    try:
                        await msg.delete()
                        print(f"[NSFW-DELETED] msg deleted in {chat.id}")
                    except Exception as e:
                        print("[NSFW DEL ERR] " + str(e))
                    
                    name = msg.from_user.first_name or "کاربر"
                    count = add_warn(chat.id, msg.from_user.id)
                    
                    # خوندن تنظیمات از دیتابیس
                    try:
                        warn_limit = int(get_setting(chat.id, "nsfw_warn_limit", "4") or "4")
                    except:
                        warn_limit = 4
                    action_type = get_setting(chat.id, "nsfw_action", "mute") or "mute"
                    duration = get_setting(chat.id, "nsfw_mute_duration", "0") or "0"
                    
                    if count >= warn_limit:
                        action_text = ""
                        try:
                            if action_type == "mute":
                                if duration == "0":
                                    until = None
                                    dur_text = "دائمی"
                                else:
                                    hours = int(duration.replace("h", ""))
                                    until = datetime.now() + timedelta(hours=hours)
                                    dur_text = str(hours) + " ساعت"
                                await chat.restrict_member(
                                    msg.from_user.id,
                                    permissions=ChatPermissions(can_send_messages=False),
                                    until_date=until
                                )
                                action_text = "به مدت " + dur_text + " سکوت شدید."
                            elif action_type == "kick":
                                await chat.ban_member(msg.from_user.id)
                                await chat.unban_member(msg.from_user.id)
                                action_text = "از گروه کیک شدید."
                            elif action_type == "ban":
                                await chat.ban_member(msg.from_user.id)
                                action_text = "از گروه بن شدید."
                        except Exception as e:
                            print("[NSFW ACTION ERR] " + str(e))
                            action_text = "(خطا در اعمال)"
                        
                        await context.bot.send_message(
                            chat_id=chat.id,
                            text="🚫 " + name + " عزیز، به دلیل ارسال محتوای نامناسب و دریافت " + str(count) + " اخطار، " + action_text
                        )
                    else:
                        remaining = warn_limit - count
                        await context.bot.send_message(
                            chat_id=chat.id,
                            text="⚠️ " + name + " عزیز، پست شما به دلیل محتوای نامناسب حذف شد. (اخطار " + str(count) + " از " + str(warn_limit) + ")"
                        )
    except Exception as e:
        print("[NSFW ERR] " + str(e))
    finally:
        for p in [temp_input, temp_jpg]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

def is_bot_owner_or_sudo(uid):
    try:
        if uid == OWNER_ID:
            return True
        if is_bot_admin(uid):
            return True
    except Exception:
        pass
    return False


async def nsfw_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker
    chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    # برای منوی اشتراک NSFW → فقط سازنده/سودو
    if action.startswith("nsub_"):
        if not is_bot_owner_or_sudo(clicker):
            await query.answer("فقط سازنده ربات", show_alert=True)
            return

    await query.answer()

    # ============ منوی اشتراک NSFW (سازنده) ============

    if action == "nsub_noop":
        return

    if action == "nsub_menu":
        try:
            await query.edit_message_text(
                "مدیریت اشتراک NSFW گروه:" + NL + NL +
                "اشتراک قفل پورن رو می تونی تمدید یا غیرفعال کنی.",
                reply_markup=build_nsfw_sub_menu(owner, chat_id)
            )
        except Exception:
            pass
        return

    if action == "nsub_toggle":
        sub = get_nsfw_sub(chat_id)
        new_enabled = 0 if sub["enabled"] else 1
        set_nsfw_sub(chat_id, sub["expire_date"], new_enabled)
        try:
            await query.edit_message_reply_markup(reply_markup=build_nsfw_sub_menu(owner, chat_id))
        except Exception:
            pass
        return

    if action == "nsub_off":
        set_nsfw_sub(chat_id, None, 0)
        try:
            await query.edit_message_text(
                "❌ اشتراک NSFW غیرفعال شد.",
                reply_markup=build_nsfw_sub_menu(owner, chat_id)
            )
        except Exception:
            pass
        return

    if action.startswith("nsub_"):
        try:
            days = int(action.replace("nsub_", ""))
        except Exception:
            return
        # محاسبه expire جدید
        current = get_nsfw_sub(chat_id)
        base_date = datetime.now()
        if current["expire_date"]:
            try:
                cur_exp = datetime.strptime(current["expire_date"], NSFW_DATE_FMT)
                if cur_exp > datetime.now():
                    base_date = cur_exp
            except Exception:
                pass
        new_exp = (base_date + timedelta(days=days)).strftime(NSFW_DATE_FMT)
        set_nsfw_sub(chat_id, new_exp, 1)
        try:
            await query.edit_message_text(
                "✅ اشتراک NSFW برای " + str(days) + " روز تمدید شد." + NL +
                "انقضا: " + new_exp,
                reply_markup=build_nsfw_sub_menu(owner, chat_id)
            )
        except Exception:
            pass
        return

    # ============ منوی NSFW گروه ============

    if action == "nsfw_noop":
        return

    if action == "nsfw_menu":
        try:
            await query.edit_message_text(
                "⚙️ تنظیمات NSFW (مالک گروه):",
                reply_markup=build_nsfw_menu(owner, chat_id)
            )
        except Exception:
            pass
        return
    
    if action == "nsub_menu":
        try:
            await query.edit_message_text(
                "👤 اشتراک NSFW (سازنده):" + NL + NL + "برای فعال‌سازی اشتراک، با پشتیبانی تماس بگیرید.",
                reply_markup=build_nsfw_sub_menu(owner, chat_id)
            )
        except Exception:
            pass
        return
    
        try:
            await query.edit_message_text(
                "تنظیمات فیلتر پورن (NSFW):",
                reply_markup=build_nsfw_menu(owner, chat_id)
            )
        except Exception:
            pass
        return

    if action == "nsfw_toggle":
        if not is_nsfw_sub_activated(chat_id):
            await query.answer("اشتراک NSFW فعال نیست", show_alert=True)
            return
        new_state = not is_group_toggle_on(chat_id)
        set_group_toggle(chat_id, new_state)
        try:
            await query.edit_message_reply_markup(reply_markup=build_nsfw_menu(owner, chat_id))
        except Exception:
            pass
        return

    if action.startswith("nsfw_sens_"):
        sens = action.replace("nsfw_sens_", "")
        if sens in SENS_LABELS:
            set_setting(chat_id, "nsfw_sensitivity", sens)
            try:
                await query.edit_message_reply_markup(reply_markup=build_nsfw_menu(owner, chat_id))
            except Exception:
                pass
        return

    # ورود به منوی پیشرفته
    if action == "nsfw_adv":
        print("[NSFW ADV] درخواست باز کردن منوی پیشرفته از " + str(clicker))
        try:
            txt = "⚙️ تنظیمات NSFW پیشرفته\n" + NL + "\n" + "اینجا می‌تونی تعداد اخطار، نوع برخورد و مدت زمان سکوت رو تنظیم کنی:"
            kb = build_nsfw_advanced_menu(owner, chat_id)
            print("[NSFW ADV] menu ساخته شد")
            await query.edit_message_text(txt, reply_markup=kb)
            print("[NSFW ADV] پیام فرستاده شد")
        except Exception as e:
            print("[NSFW ADV ERR] " + str(e))
            import traceback
            traceback.print_exc()
        return

    # تعداد اخطار
    if action.startswith("nsfw_limit_"):
        try:
            limit = action.replace("nsfw_limit_", "").split(":")[0]
            set_setting(chat_id, "nsfw_warn_limit", limit)
            await query.answer("✅ تعداد اخطار: " + limit)
            await query.edit_message_reply_markup(reply_markup=build_nsfw_advanced_menu(owner, chat_id))
        except Exception as e:
            print("[NSFW LIMIT ERR] " + str(e))
        return

    # نوع برخورد
    if action.startswith("nsfw_action_"):
        try:
            act = action.replace("nsfw_action_", "").split(":")[0]
            if act in ["mute", "kick", "ban"]:
                set_setting(chat_id, "nsfw_action", act)
                await query.answer("✅ نوع برخورد: " + act)
                await query.edit_message_reply_markup(reply_markup=build_nsfw_advanced_menu(owner, chat_id))
        except Exception as e:
            print("[NSFW ACTION ERR] " + str(e))
        return

    # مدت زمان
    if action.startswith("nsfw_dur_"):
        try:
            dur = action.replace("nsfw_dur_", "").split(":")[0]
            set_setting(chat_id, "nsfw_mute_duration", dur)
            await query.answer("✅ مدت: " + dur)
            await query.edit_message_reply_markup(reply_markup=build_nsfw_advanced_menu(owner, chat_id))
        except Exception as e:
            print("[NSFW DUR ERR] " + str(e))
        return

    # noop
    if action == "nsfw_noop":
        await query.answer()
        return


def register(app):
    app.add_handler(
        MessageHandler(filters.PHOTO | filters.ANIMATION | filters.VIDEO | filters.Sticker.ALL | filters.Document.ALL, check_nsfw, block=False),
        group=20
    )
    app.add_handler(CallbackQueryHandler(nsfw_cb_handler, pattern="^(nsfw_|nsub_)"), group=-150)
