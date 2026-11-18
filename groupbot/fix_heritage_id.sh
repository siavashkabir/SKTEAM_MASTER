#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# chat_id اشتباه و درست
WRONG = -10044639682429
RIGHT = -1004463882429

print(f"═══ قبل از fix ═══")
c.execute("SELECT chat_id, title FROM groups WHERE chat_id=?", (WRONG,))
print(f"گروه اشتباه: {c.fetchone()}")
c.execute("SELECT COUNT(*) FROM members WHERE chat_id=?", (WRONG,))
print(f"اعضای گروه اشتباه: {c.fetchone()[0]}")
print()

# ★ fix گروه اصلی
c.execute("UPDATE groups SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
print(f"✅ groups: {c.rowcount} ردیف آپدیت")

# ★ fix اعضا
c.execute("UPDATE members SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
print(f"✅ members: {c.rowcount} ردیف آپدیت")

# ★ fix ادمین‌ها
c.execute("UPDATE group_admins SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
print(f"✅ group_admins: {c.rowcount} ردیف آپدیت")

# ★ fix perms
for table in ['user_perms', 'deputy_perms', 'admin_permissions']:
    try:
        c.execute(f"UPDATE {table} SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
        print(f"✅ {table}: {c.rowcount} ردیف آپدیت")
    except Exception as e:
        print(f"⚠️ {table}: {e}")

# ★ fix subscriptions
try:
    c.execute("UPDATE subscriptions SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
    print(f"✅ subscriptions: {c.rowcount} ردیف آپدیت")
except Exception as e:
    print(f"⚠️ subscriptions: {e}")

# ★ fix settings
try:
    c.execute("UPDATE settings SET chat_id=? WHERE chat_id=?", (RIGHT, WRONG))
    print(f"✅ settings: {c.rowcount} ردیف آپدیت")
except Exception as e:
    print(f"⚠️ settings: {e}")

conn.commit()
print()
print("═══ بعد از fix ═══")
c.execute("SELECT chat_id, title FROM groups WHERE chat_id=?", (RIGHT,))
print(f"گروه درست: {c.fetchone()}")
c.execute("SELECT COUNT(*) FROM members WHERE chat_id=?", (RIGHT,))
print(f"اعضای گروه درست: {c.fetchone()[0]}")

conn.close()
PYEOF

echo ""
echo "═══ تست ═══"
python3 -c "
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    for cid in [-1004463882429]:
        try:
            chat = await bot.get_chat(cid)
            print(f'✅ {cid}: {chat.title}')
            admins = await bot.get_chat_administrators(cid)
            print(f'   ادمین‌ها: {len(admins)}')
        except Exception as e:
            print(f'❌ {cid}: {e}')
    await bot.close()

asyncio.run(test())
"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 حالا برو تلگرام:"
echo "1. توی گروه HERITAGE «پیکربندی» بزن"
echo "2. باید ادمین‌ها رو نشون بده"
echo "═══════════════════════════════════════════════════"
