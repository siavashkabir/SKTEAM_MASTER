import os

print("="*80)
print("🔍 کد هندلرهای osub_manager و osub_manual_ok_")
print("="*80)

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === 1. هندلر osub_manager ===
print("\n=== 1. هندلر osub_manager (خط 2264) ===")
for i, line in enumerate(lines):
    if 'action.startswith("osub_manager")' in line:
        for j in range(i, min(i+40, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
        break

# === 2. هندلر osub_manual_ok_ ===
print("\n" + "="*80)
print("=== 2. هندلر osub_manual_ok_ (خط 2314) ===")
for i, line in enumerate(lines):
    if 'action.startswith("osub_manual_ok_")' in line:
        for j in range(i, min(i+45, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
        break

# === 3. جستجوی فاکتور و send_message به OWNER_ID در همه جا ===
print("\n" + "="*80)
print("=== 3. هر جا که به OWNER_ID پیام فرستاده می‌شود (با متن) ===")
for i, line in enumerate(lines):
    if 'send_message' in line and 'OWNER_ID' in line:
        start = max(0, i-15)
        for j in range(start, i+3):
            print(f"   {j+1}: {lines[j].rstrip()}")
        print("   ---")
