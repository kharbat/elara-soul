#!/bin/bash
# rebuild-site.sh — Rebuild Elara's website from the soul directory
# Called by cron or manually after changes

cd /home/kharbat/soul
python3 site/build.py
echo "[$(date)] Site rebuilt — $(ls docs/*.html | wc -l) pages" >> system/heartbeats.log
