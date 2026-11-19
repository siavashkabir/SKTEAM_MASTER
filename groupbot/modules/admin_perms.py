from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_all_perms, set_admin_perm, get_admin_perm

PERMS = [
    ('locks',    '🔒 قفل‌های اصلی'),
    ('media',    '📸 قفل‌های رسانه'),
    ('welcome',  '👋 خوش‌آمدگویی'),
    ('nsfw',     '🔞 NSFW'),
    ('warn',     '⚠️ هشدار'),
    ('purge',    '🧹 پاک‌سازی'),
    ('link',     '🔗 لینک'),
    ('vip',      '⭐ اعضای ویژه'),
    ('nickname', '🏷️ تنظیم لقب'),
    ('config',   '⚙️ پیکربندی'),
]


def admin_list_menu(uid, chat_id, admins):
    print(f"[ADMIN_LIST DBG] uid={uid}, chat_id={chat_id}, admins_count={len(admins)}")
    print(f"[ADMIN_LIST DBG] admins={admins}")
    """لیست ادمین‌ها"""
    btns = []
    for a in admins:
        name = a.get('name', 'ادمین')
        aid = a.get('user_id', 0)
        btns.append([InlineKeyboardButton("👤 " + name, callback_data="aperm_user:" + str(aid) + ":" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="op_manage:" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(btns)


def deputy_list_menu(uid, chat_id, deputies):
    """لیست معاونین"""
    btns = []
    for d in deputies:
        name = d.get('name', 'معاون')
        did = d.get('user_id', 0)
        btns.append([InlineKeyboardButton("👤 " + name, callback_data="dperm_user:" + str(did) + ":" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="op_manage:" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(btns)


def perms_menu(uid, chat_id, target_id, role):
    """لیست دسترسی‌های یه ادمین/معاون"""
    perms = get_all_perms(chat_id, target_id)
    btns = []
    for key, label in PERMS:
        mark = "✅ " if perms.get(key, False) else "⬜ "
        prefix = "aperm_tgl_" if role == "admin" else "dperm_tgl_"
        btns.append([InlineKeyboardButton(mark + label, callback_data=prefix + key + ":" + str(target_id) + ":" + str(uid) + ":" + str(chat_id))])
    back_prefix = "aperm_list:" if role == "admin" else "dperm_list:"
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data=back_prefix + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(btns)


def get_admins_list(chat_id):
    """گرفتن لیست ادمین‌ها از دیتابیس"""
    from database import get_all_deputies
    # این تابع باید ادمین‌ها رو از جدول برگردونه
    # فعلاً از یه تابع فرضی استفاده می‌کنیم
    try:
        from database import get_group_admins
        return get_group_admins(chat_id)
    except Exception:
        return []


def add_admin_to_db(chat_id, user_id, name):
    """اضافه کردن ادمین به دیتابیس"""
    import turso_db as sqlite3
    from config import DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS group_admins (chat_id INTEGER, user_id INTEGER, name TEXT, PRIMARY KEY (chat_id, user_id))")
    c.execute("INSERT OR REPLACE INTO group_admins (chat_id, user_id, name) VALUES (?, ?, ?)", (chat_id, user_id, name))
    conn.commit()
    conn.close()


def get_group_admins_list(chat_id):
    """گرفتن لیست ادمین‌ها"""
    import turso_db as sqlite3
    from config import DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT user_id, name FROM group_admins WHERE chat_id=?", (chat_id,))
        rows = c.fetchall()
    except Exception:
        rows = []
    conn.close()
    return [{'user_id': r[0], 'name': r[1]} for r in rows]
