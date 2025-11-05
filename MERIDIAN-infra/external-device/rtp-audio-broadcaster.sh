#!/usr/bin/env bash
set -euo pipefail

MONITOR="${MONITOR:?Set MONITOR (e.g. alsa_output...monitor)}"
PI_IP="${PI_IP:?Set PI_IP (e.g. 192.168.0.22)}"
PORT="${PORT:-5004}"
BITRATE="${BITRATE:-64k}"   # Opus bitrate

echo "Streaming '$MONITOR' to rtp://$PI_IP:$PORT (Opus @$BITRATE)…"
exec ffmpeg -hide_banner -loglevel error \
  -f pulse -i "$MONITOR" \
  -ac 1 -ar 48000 -c:a libopus -b:a "$BITRATE" \
  -f rtp "rtp://$PI_IP:$PORT"