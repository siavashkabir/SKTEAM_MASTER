#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🔍 وضعیت Ubuntu + Music Player"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ۱. آیا پوشه music_player هست؟ ───"
proot-distro login ubuntu -- bash -c "
ls -la ~/music_player/ 2>/dev/null && echo '✅ پوشه هست' || echo '❌ پوشه نیست'
echo ''
echo '─── ۲. آیا venv ساخته شده؟ ───'
ls -la ~/music_player/venv/bin/python3 2>/dev/null && echo '✅ venv هست' || echo '❌ venv نیست'
echo ''
echo '─── ۳. پکیج‌های نصب شده ───'
if [ -d ~/music_player/venv ]; then
    source ~/music_player/venv/bin/activate
    pip list 2>/dev/null | grep -iE 'pyrogram|tgcalls|ntgcalls|aiohttp|dotenv'
fi
echo ''
echo '─── ۴. تست import ───'
if [ -d ~/music_player/venv ]; then
    source ~/music_player/venv/bin/activate
    python3 -c \"
try:
    import pyrogram
    print('✅ pyrogram:', pyrogram.__version__)
except Exception as e:
    print('❌ pyrogram:', e)
try:
    import pytgcalls
    print('✅ pytgcalls: OK')
except Exception as e:
    print('❌ pytgcalls:', e)
try:
    import ntgcalls
    print('✅ ntgcalls: OK')
except Exception as e:
    print('❌ ntgcalls:', e)
\"
fi
" 2>&1

echo ""
echo "═══════════════════════════════════════════════════"
