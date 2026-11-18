# -*- coding: utf-8 -*-
"""log_hooks - توابع کمکی برای ثبت رخدادها"""
async def log_ban(context, chat_id, actor_id, actor_name, target_id, target_name, reason=""):
    try:
        from modules.logger import log_event
        await log_event(context, "ban", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id,
                        target_name=target_name, details=reason)
    except Exception as e: print("[HOOK BAN ERR] " + str(e))

async def log_mute(context, chat_id, actor_id, actor_name, target_id, target_name, duration="", reason=""):
    try:
        from modules.logger import log_event
        det = ("مدت: " + str(duration)) if duration else ""
        if reason: det += " | دلیل: " + str(reason)
        await log_event(context, "mute", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id,
                        target_name=target_name, details=det)
    except Exception as e: print("[HOOK MUTE ERR] " + str(e))

async def log_warn(context, chat_id, actor_id, actor_name, target_id, target_name, count="", reason=""):
    try:
        from modules.logger import log_event
        det = ("اخطار شماره: " + str(count)) if count else ""
        if reason: det += " | دلیل: " + str(reason)
        await log_event(context, "warn", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id,
                        target_name=target_name, details=det)
    except Exception as e: print("[HOOK WARN ERR] " + str(e))

async def log_kick(context, chat_id, actor_id, actor_name, target_id, target_name, reason=""):
    try:
        from modules.logger import log_event
        await log_event(context, "kick", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id,
                        target_name=target_name, details=reason)
    except Exception as e: print("[HOOK KICK ERR] " + str(e))

async def log_purge(context, chat_id, actor_id, actor_name, count=0, scope="گروه"):
    try:
        from modules.logger import log_event
        await log_event(context, "purge", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, details="تعداد: " + str(count) + " | " + str(scope))
    except Exception as e: print("[HOOK PURGE ERR] " + str(e))

async def log_lock(context, chat_id, actor_id, actor_name, lock_name, enabled):
    try:
        from modules.logger import log_event
        act = "lock" if enabled else "unlock"
        await log_event(context, act, chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, details="قفل: " + str(lock_name))
    except Exception as e: print("[HOOK LOCK ERR] " + str(e))

async def log_badword(context, chat_id, target_id, target_name, word=""):
    try:
        from modules.logger import log_event
        await log_event(context, "badword", chat_id=chat_id, target_id=target_id,
                        target_name=target_name, details="کلمه: " + str(word)[:50])
    except Exception as e: print("[HOOK BW ERR] " + str(e))

async def log_spam(context, chat_id, target_id, target_name, count=0):
    try:
        from modules.logger import log_event
        await log_event(context, "spam", chat_id=chat_id, target_id=target_id,
                        target_name=target_name, details="پیام‌ها: " + str(count))
    except Exception as e: print("[HOOK SPAM ERR] " + str(e))

async def log_anti_raid(context, chat_id, target_id, target_name, info=""):
    try:
        from modules.logger import log_event
        await log_event(context, "raid", chat_id=chat_id, target_id=target_id,
                        target_name=target_name, details=info)
    except Exception as e: print("[HOOK RAID ERR] " + str(e))

async def log_nsfw(context, chat_id, target_id, target_name, info=""):
    try:
        from modules.logger import log_event
        await log_event(context, "nsfw", chat_id=chat_id, target_id=target_id,
                        target_name=target_name, details=info)
    except Exception as e: print("[HOOK NSFW ERR] " + str(e))

async def log_join(context, chat_id, user_id, user_name):
    try:
        from modules.logger import log_event
        await log_event(context, "join", chat_id=chat_id, target_id=user_id, target_name=user_name)
    except Exception as e: print("[HOOK JOIN ERR] " + str(e))

async def log_leave(context, chat_id, user_id, user_name, forced=False):
    try:
        from modules.logger import log_event
        act = "fkick" if forced else "leave"
        await log_event(context, act, chat_id=chat_id, target_id=user_id, target_name=user_name)
    except Exception as e: print("[HOOK LEAVE ERR] " + str(e))

async def log_admin_add(context, chat_id, actor_id, actor_name, target_id, target_name, perms=""):
    try:
        from modules.logger import log_event
        await log_event(context, "admin_add", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id,
                        target_name=target_name, details=perms)
    except Exception as e: print("[HOOK AA ERR] " + str(e))

async def log_admin_del(context, chat_id, actor_id, actor_name, target_id, target_name):
    try:
        from modules.logger import log_event
        await log_event(context, "admin_del", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, target_id=target_id, target_name=target_name)
    except Exception as e: print("[HOOK AD ERR] " + str(e))

async def log_fj_add(context, actor_id, actor_name, link, name):
    try:
        from modules.logger import log_event
        await log_event(context, "fj_add", actor_id=actor_id, actor_name=actor_name,
                        details="لینک: " + str(link) + " | نام: " + str(name))
    except Exception as e: print("[HOOK FJA ERR] " + str(e))

async def log_fj_del(context, actor_id, actor_name, name):
    try:
        from modules.logger import log_event
        await log_event(context, "fj_del", actor_id=actor_id, actor_name=actor_name,
                        details="حذف: " + str(name))
    except Exception as e: print("[HOOK FJD ERR] " + str(e))

async def log_setting_change(context, chat_id, actor_id, actor_name, setting, old_val="", new_val=""):
    try:
        from modules.logger import log_event
        det = "تنظیم: " + str(setting) + " | " + str(old_val) + " → " + str(new_val)
        await log_event(context, "setting_change", chat_id=chat_id, actor_id=actor_id,
                        actor_name=actor_name, details=det)
    except Exception as e: print("[HOOK SET ERR] " + str(e))

async def log_sub(context, chat_id, group_name, sub_type, duration, price=0, action="sub_new"):
    try:
        from modules.logger import log_event
        det = "گروه: " + str(group_name) + " | نوع: " + str(sub_type) + " | مدت: " + str(duration)
        if price: det += " | قیمت: " + str(price)
        await log_event(context, action, chat_id=chat_id, details=det)
    except Exception as e: print("[HOOK SUB ERR] " + str(e))

async def log_sys(context, msg):
    try:
        from modules.logger import log_event
        await log_event(context, "sys", details=msg)
    except Exception as e: print("[HOOK SYS ERR] " + str(e))

async def log_err(context, err):
    try:
        from modules.logger import log_event
        await log_event(context, "err", details=str(err)[:200])
    except Exception as e: print("[HOOK ERR ERR] " + str(e))
