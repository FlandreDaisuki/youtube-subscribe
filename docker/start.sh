#!/bin/sh

cat << EOF > /usr/local/bin/ytsub
#!/bin/sh

python3 /ytsub/main.py "\$@"
EOF

chmod +x /usr/local/bin/ytsub

echo 'Start running youtube-subscribe services...'
echo "$CRON_FREQ /usr/local/bin/ytsub dl --sync >> /root/cron.log 2>&1" > /var/spool/cron/crontabs/root
crond -l 2 -f
