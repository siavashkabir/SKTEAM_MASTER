#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ نقش‌ها — $(date)"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. ADMIN_PERMS ═══"
grep -n "ADMIN_PERMS = \[" "$AC"
START=$(grep -n "ADMIN_PERMS = \[" "$AC" | head -1 | cut -d: -f1)
END=$(grep -n "\]" "$AC" | awk -F: -v s=$START '$1 > s {print $1; exit}')
sed -n "${START},${END}p" "$AC"
echo ""

echo "═══ ۲. DEPUTY_PERMS ═══"
START=$(grep -n "DEPUTY_PERMS = \[" "$AC" | head -1 | cut -d: -f1)
END=$(grep -n "\]" "$AC" | awk -F: -v s=$START '$1 > s {print $1; exit}')
sed -n "${START},${END}p" "$AC"
echo ""

echo "═══ ۳. VIP_PERMS ═══"
START=$(grep -n "VIP_PERMS = \[" "$AC" | head -1 | cut -d: -f1)
END=$(grep -n "\]" "$AC" | awk -F: -v s=$START '$1 > s {print $1; exit}')
sed -n "${START},${END}p" "$AC"
echo ""

echo "═══ ۴. get_target_role — چطور نقش رو تشخیص می‌ده ═══"
START=$(grep -n "def get_target_role" "$AC" | head -1 | cut -d: -f1)
sed -n "${START},$((START+25))p" "$AC"
echo ""

echo "═══ ۵. build_access_menu — کل تابع ═══"
START=$(grep -n "def build_access_menu" "$AC" | head -1 | cut -d: -f1)
END=$(grep -n "^def \|^async def " "$AC" | awk -F: -v s=$START '$1 > s {print $1; exit}')
echo "از خط $START تا $END"
sed -n "${START},${END}p" "$AC"
echo ""

echo "═══ ۶. role_label — چطور نمایش می‌ده ═══"
START=$(grep -n "def role_label" "$AC" | head -1 | cut -d: -f1)
sed -n "${START},$((START+15))p" "$AC"
echo ""

echo "═══ ۷. دیتابیس: نقش‌های فعلی گروه تست ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# admin_permissions
c.execute("SELECT * FROM admin_permissions WHERE chat_id=-1004349813270")
print("=== admin_permissions ===")
for r in c.fetchall(): print(f"  {r}")
print()

# user_perms
c.execute("SELECT * FROM user_perms WHERE chat_id=-1004349813270")
print("=== user_perms ===")
for r in c.fetchall(): print(f"  {r}")
print()

# deputy_perms
c.execute("SELECT * FROM deputy_perms WHERE chat_id=-1004349813270 LIMIT 20")
print("=== deputy_perms ===")
for r in c.fetchall(): print(f"  {r}")

conn.close()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_ROLES.txt

echo ""
echo "✅ فایل: ~/DIAG_ROLES.txt"
echo "📏 خطوط: $(wc -l < ~/DIAG_ROLES.txt)"
