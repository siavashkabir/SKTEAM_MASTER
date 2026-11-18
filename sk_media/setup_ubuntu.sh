#!/bin/bash
mkdir -p /root/sk_media/cache
cd /root/sk_media
python3 -m py_compile player.py && echo "✅ compile OK" || echo "❌ compile FAIL"
