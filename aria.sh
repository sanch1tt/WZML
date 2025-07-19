#!/bin/bash
tracker_list=$(curl -s https://ngosang.github.io/trackerslist/trackers_all_http.txt | awk '$0' | tr '\n\n' ',')
aria2c \
  --enable-rpc=true \
  --rpc-listen-all=false \
  --rpc-allow-origin-all=true \
  --rpc-listen-port=6800 \
  --bt-tracker="${tracker_list}" \
  --max-connection-per-server=10 \
  --split=10 \
  --max-concurrent-downloads=5 \
  --continue=true \
  --check-certificate=false \
  --follow-torrent=mem \
  --summary-interval=0 \
  --quiet=true \
  --seed-ratio=0 \
  --max-upload-limit=1K \
  -D