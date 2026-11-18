#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
SS=modules/shared_state.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_cache_$TS"
cp "$SS" "$SS.bak_cache_$TS"
echo "✅ بک‌آپ گرفته شد"

source venv/bin/activate

# ۱. اضافه کردن PROMOTE_PERMS به shared_state
python3 << 'PYEOF'
SS = "/data/data/com.termux/files/home/groupbot/modules/shared_state.py"
with open(SS, "r", encoding="utf-8") as f:
    content = f.read()

if "PROMOTE_PERMS" not in content:
    content += "\n# ★ cache جدا برای perms پنل افزودن مدیر\nPROMOTE_PERMS = {}\n"
    with open(SS, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ PROMOTE_PERMS به shared_state اضافه شد")
else:
    print("⚠️ از قبل هست")
PYEOF

# ۲. fix start.py
python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"
with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# import
if "from modules.shared_state import PROMOTE_WAIT, PROMOTE_PERMS" not in content:
    content = content.replace(
        "from modules.shared_state import PROMOTE_WAIT",
        "from modules.shared_state import PROMOTE_WAIT, PROMOTE_PERMS",
        1
    )
    print("✅ import PROMOTE_PERMS")

# pm_toggle: ذخیره در cache
old_t = '''    perm_name = action.replace("pm_toggle_", "")
    
    if perm_name in PROMOTE_WAIT[uid]["perms"]:
        PROMOTE_WAIT[uid]["perms"][perm_name] = not PROMOTE_WAIT[uid]["perms"][perm_name]
    
    perms = PROMOTE_WAIT[uid]["perms"]'''

new_t = '''    perm_name = action.replace("pm_toggle_", "")
    
    if perm_name in PROMOTE_WAIT[uid]["perms"]:
        PROMOTE_WAIT[uid]["perms"][perm_name] = not PROMOTE_WAIT[uid]["perms"][perm_name]
    
    perms = PROMOTE_WAIT[uid]["perms"]
    # ★ کپی توی cache جدا
    PROMOTE_PERMS[uid] = dict(perms)
    print(f"[PM_TOGGLE] cached {len(perms)} perms for uid={uid}")'''

if old_t in content:
    content = content.replace(old_t, new_t, 1)
    print("✅ pm_toggle cache")

# pm_confirm: خوندن از cache
old_c = '''            _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})'''
new_c = '''            _perms = PROMOTE_PERMS.get(uid, {})
            print(f"[PM_CONFIRM] from cache: {len(_perms)} perms for uid={uid}")'''

if old_c in content:
    content = content.replace(old_c, new_c, 1)
    print("✅ pm_confirm cache")
else:
    print("⚠️ pm_confirm الگو نبود")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1 && python3 -m py_compile "$SS" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_cache_$TS" "$ST"
    cp "$SS.bak_cache_$TS" "$SS"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix cache انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام تست کن و این رو بزن:"
echo "tail -n 50 ~/groupbot_bot.log | grep -E 'PM_TOGGLE|PM_CONFIRM'"
echo "═══════════════════════════════════════════════════"
