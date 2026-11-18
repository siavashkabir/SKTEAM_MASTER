#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تحلیل خواندنی منوها — هیچ تغییری در کد نمی‌دهد"""
import re, subprocess
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "groupbot"
MODULES = PROJECT / "modules"
REPORT = PROJECT / "READONLY_MENU_MAP.md"

FILES = ["start.py", "pv_main.py", "owner_set_group.py",
         "system_management.py", "remote_groups.py",
         "force_join.py", "reply.py"]

out = []
def p(s=""):
    out.append(str(s))

def _find_func(lines, name):
    """پیدا کردن تابع و برگرداندن خطوطش"""
    for i, l in enumerate(lines):
        if re.match(r'\s*def\s+' + re.escape(name) + r'\s*\(', l):
            # تا خطوط بعدی که def دیگه‌ای میاد یا ۱۰۰ خط
            start = i
            indent = len(l) - len(l.lstrip())
            end = min(len(lines), i + 150)
            for j in range(i+1, end):
                ln = lines[j]
                if ln.strip() and (len(ln) - len(ln.lstrip())) <= indent and re.match(r'\s*def\s+', ln):
                    end = j
                    break
            return start, end
    return None, None

def _extract_buttons(block):
    """استخراج دکمه‌ها از یک بلوک کد"""
    btns = []
    # هر InlineKeyboardButton
    for m in re.finditer(r'InlineKeyboardButton\s*\(\s*["\']([^"\']+)["\']\s*,\s*callback_data\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|f["\']([^"\']+)["\'])', block):
        label = m.group(1)
        cb = m.group(2) or m.group(3) or m.group(4) or "?"
        btns.append((label, cb))
    return btns

p("# نقشه منوها (فقط خواندنی)")
p("")
p("تاریخ: " + str(datetime.now()))
p("")
p("> این گزارش فقط برای تحلیل ساخته شده — هیچ کدی تغییر نکرده.")
p("")

# ══════════════════════════════════════════════════
# بخش ۱ — منوهای اصلی
# ══════════════════════════════════════════════════
MAIN_MENUS = [
    "sudo_panel_menu",         # منوی سازنده/سودو (PV)
    "group_panel_for_sudo",    # منوی گروه برای سازنده/سودو
    "group_owner_panel_menu",  # منوی مالک گروه
    "group_owner_panel_old",   # منوی قدیمی مالک
    "owner_section_menu",      # بخش سازنده
    "group_panel_menu",        # منوی گروه (عمومی)
    "group_settings_menu",     # تنظیمات گروه
    "group_manage_menu",       # مدیریت گروه
    "owner_botadmins_menu",    # مدیریت ادمین‌های ربات
    "pv_menu",                 # منوی PV
    "pv_chat_menu",            # منوی چت
    "main_menu_kb",            # کیبورد PV در pv_main
    "shop_menu_kb",            # کیبورد فروشگاه
]

p("---")
p("")
p("## 🏠 بخش ۱ — منوهای اصلی")
p("")

for mn in MAIN_MENUS:
    p("")
    p("### `" + mn + "`")
    p("")
    found_any = False
    for fn in FILES:
        fp = MODULES / fn
        if not fp.exists(): continue
        text = fp.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        s, e = _find_func(lines, mn)
        if s is None: continue
        found_any = True
        block = "\n".join(lines[s:e])
        p("**فایل:** `" + fn + "` (خط " + str(s+1) + ")")
        p("")
        btns = _extract_buttons(block)
        if btns:
            p("**دکمه‌ها:**")
            p("")
            for lbl, cb in btns:
                p("- `" + lbl + "`  →  `" + cb + "`")
        else:
            p("_(هیچ دکمه‌ای در این تابع پیدا نشد)_")
        p("")
    if not found_any:
        p("❌ تابع پیدا نشد")
        p("")

# ══════════════════════════════════════════════════
# بخش ۲ — زیرمنوهای بخش سازنده
# ══════════════════════════════════════════════════
p("---")
p("")
p("## 🔧 بخش ۲ — زیرمنوهای بخش سازنده")
p("")
p("این زیرمنوها از منوی `owner_section_menu` قابل دسترسی هستن:")
p("")

SUB_MENUS = [
    # زیرمنوهای s_fj (جوین اجباری)
    ("s_fj_menu", "جوین اجباری"),
    # زیرمنوهای s_op (ادمین‌های ربات)
    ("s_op_botadmins", "مدیریت ادمین‌های ربات"),
    ("s_op_ba_list", "لیست ادمین‌ها"),
    # زیرمنوهای s_ba (permissions)
    ("s_ba_perm", "دسترسی‌های ادمین"),
    ("s_ba_del", "حذف ادمین"),
    # زیرمنوهای آماری
    ("s_op_sudo_stats", "آمار سودوها"),
    ("s_op_group_stats", "آمار گروه‌ها"),
    # مدیریت گروه‌ها
    ("rmt_groups", "مدیریت گروه‌ها"),
    ("rmt_g", "گروه انتخاب‌شده"),
    # پنل گروه
    ("s_panel_group", "ورود به پنل گروه"),
]

for cb_name, desc in SUB_MENUS:
    p("")
    p("### " + desc + " (`" + cb_name + "`)")
    p("")
    # جستجوی این callback در همه فایل‌ها
    for fn in FILES:
        fp = MODULES / fn
        if not fp.exists(): continue
        text = fp.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        hits = []
        for i, l in enumerate(lines):
            if '"' + cb_name + '"' in l or "'" + cb_name + "'" in l:
                hits.append(i)
        if not hits: continue
        # فقط if action
        action_hits = [i for i in hits if "if action ==" in lines[i]]
        if action_hits:
            p("**فایل:** `" + fn + "`")
            p("")
            for h in action_hits[:3]:
                # پیدا کردن دکمه‌ها در ۵۰ خط بعدی
                end = min(len(lines), h+80)
                block = "\n".join(lines[h:end])
                btns = _extract_buttons(block)
                if btns:
                    p("دکمه‌های این زیرمنو:")
                    p("")
                    for lbl, cb in btns:
                        p("- `" + lbl + "`  →  `" + cb + "`")
                    p("")

# ══════════════════════════════════════════════════
# بخش ۳ — همه callback ها با لیبل فارسی
# ══════════════════════════════════════════════════
p("---")
p("")
p("## 📋 بخش ۳ — همه دکمه‌ها با لیبل و callback")
p("")

all_btns = {}
for fn in FILES:
    fp = MODULES / fn
    if not fp.exists(): continue
    text = fp.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'InlineKeyboardButton\s*\(\s*["\']([^"\']+)["\']\s*,\s*callback_data\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|f["\']([^"\']+)["\'])', text):
        label = m.group(1)
        cb = m.group(2) or m.group(3) or m.group(4) or "?"
        # پاکسازی f-string
        cb_clean = re.sub(r'\{[^}]+\}', ':*', cb)
        all_btns.setdefault(cb_clean, set()).add(label)

p("| callback (پاک‌سازی‌شده) | لیبل‌های دیده‌شده |")
p("|---|---|")
for cb in sorted(all_btns.keys()):
    labels = " / ".join(sorted(all_btns[cb])[:3])
    p("| `" + cb + "` | " + labels + " |")
p("")

# ══════════════════════════════════════════════════
# بخش ۴ — منطق نمایش بر اساس نقش
# ══════════════════════════════════════════════════
p("---")
p("")
p("## 🎭 بخش ۴ — منطق نمایش بر اساس نقش")
p("")
p("این بخش نشان می‌دهد کد چطور بین سازنده/سودو/مالک گروه/ادمین تفاوت می‌گذارد:")
p("")

# جستجوی is_bot_owner_or_sudo / is_bot_admin / OWNER_ID در توابع منو
for fn in ["start.py"]:
    fp = MODULES / fn
    if not fp.exists(): continue
    text = fp.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    # بلوک‌هایی که is_bot_owner_or_sudo / is_bot_admin دارن
    for i, l in enumerate(lines):
        if ("is_bot_owner_or_sudo" in l or "is_bot_admin" in l) and "def " not in l:
            # یه پنجره ۳۰ خطی
            end = min(len(lines), i+30)
            ctx_text = "\n".join(lines[i:end])
            # فقط اگه توی یه تابع منو باشه
            # پیدا کردن نام تابع بالاتر
            fn_name = None
            for j in range(i, max(0, i-200), -1):
                mm = re.match(r'\s*def\s+(\w+)\s*\(', lines[j])
                if mm:
                    fn_name = mm.group(1)
                    break
            if fn_name and ("menu" in fn_name or "panel" in fn_name):
                p("**`" + fn_name + "`** — خط " + str(i+1) + ":")
                p("")
                p("```python")
                for k, cl in enumerate(lines[i:i+12], start=i+1):
                    p(str(k).rjust(5) + " | " + cl.rstrip())
                p("```")
                p("")

# ══════════════════════════════════════════════════
# ذخیره
# ══════════════════════════════════════════════════
REPORT.write_text("\n".join(out), encoding="utf-8")

print("✅ گزارش: " + str(REPORT))
print("📊 " + str(REPORT.stat().st_size) + " بایت")
print("📝 " + str(len(out)) + " خط")
print("")
print("⚠️  هیچ کدی تغییر نکرد — فقط خواندنی")
print("")

# کپی به Download
try:
    subprocess.run(["cp", str(REPORT), "/sdcard/Download/READONLY_MENU_MAP.md"], check=True)
    print("📱 /sdcard/Download/READONLY_MENU_MAP.md")
    print("")
    print("حالا از Files → Download بازش کن و متن رو برام بفرست")
except Exception as e:
    print("⚠️  " + str(e))
    print("دستی: cp " + str(REPORT) + " /sdcard/Download/")
