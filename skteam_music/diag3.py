import re
from pathlib import Path

with open("bot.py", encoding="utf-8") as f:
    lines = f.readlines()

# ۱. handler های مربوط به mention/اسم/صدا زدن
print("═══ ۱. handler های mention / صدا زدن ═══")
for i, l in enumerate(lines, 1):
    if any(k in l.lower() for k in ["mention", "صدا زدن", "صداش", "reply_to_message.from_user.id == ", "is_bot_mentioned"]):
        print(f"  {i}: {l.strip()[:110]}")

# ۲. سطرهای مربوط به bot mention
print("\n═══ ۲. الگوهای شکار پیام ═══")
for i, l in enumerate(lines, 1):
    if "is_music_auth" in l or "is_bot_owner" in l or "is_sk_owner" in l:
        print(f"  {i}: {l.strip()[:110]}")

# ۳. پیام‌های جواب ربات
print("\n═══ ۳. جواب‌های طنز / صدا زدن ═══")
for i, l in enumerate(lines, 1):
    if any(k in l for k in ["سیاوش", "siavash", "call", "صدا", "جواب", "پاسخ"]):
        print(f"  {i}: {l.strip()[:110]}")

# ۴. همه handler های MessageHandler
print("\n═══ ۴. handler های MessageHandler ═══")
for i, l in enumerate(lines, 1):
    if "add_handler" in l and "MessageHandler" in l:
        # group چی
        g = "?"
        for j in range(max(0, i-2), min(len(lines), i+2)):
            m = re.search(r'group=(-?\d+)', lines[j])
            if m: g = m.group(1); break
        print(f"  {i}: group={g} | {l.strip()[:80]}")

# ۵. توابع با نام mention
print("\n═══ ۵. توابع mention/اسم ═══")
for i, l in enumerate(lines, 1):
    if ("def " in l or "async def" in l) and any(k in l.lower() for k in ["mention", "name", "call", "joke", "reply"]):
        print(f"  {i}: {l.strip()[:110]}")

# ۶. filter های خاص
print("\n═══ ۶. filter های خاص ═══")
for i, l in enumerate(lines, 1):
    if "filters.Regex" in l or "filters.Entity" in l or "filters.Mention" in l:
        print(f"  {i}: {l.strip()[:110]}")
