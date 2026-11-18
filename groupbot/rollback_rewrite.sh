#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
LATEST=$(ls -t "$ST".bak_rewrite_* 2>/dev/null | head -1)
echo "restore از: $LATEST"
cp "$LATEST" "$ST"
python3 -m py_compile "$ST" 2>&1 && echo "✅ سالم" || echo "❌ خراب"
