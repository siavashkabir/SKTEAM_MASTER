import re
with open("userbot_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if "async def process_join" in line:
        start = i
    if start != -1 and i > start and "def mark_join" in line:
        end = i
        break

if start == -1:
    print("❌ پیدا نشد")
else:
    for i in range(start, min(end, start+50)):
        print(f"{i+1}: {lines[i]}".rstrip())
