#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5004}"
CHANNELS="${CHANNELS:-1}"     # must match sender's -ac
ALSA_DEV="${ALSA_DEV:-default}"
MODE="${MODE:-play}"        # play | wav | pcm
OUT="${OUT:-pipe:1}"

SDP_FILE="$(mktemp)"
cleanup() { rm -f "$SDP_FILE"; }
trap cleanup EXIT

cat >"$SDP_FILE" <<SDP
v=0
o=- 0 0 IN IP4 0.0.0.0
s=Opus RTP
c=IN IP4 0.0.0.0
t=0 0
m=audio ${PORT} RTP/AVP 97
a=rtpmap:97 opus/48000/${CHANNELS}
SDP

echo "Listening for RTP (Opus) on udp://0.0.0.0:${PORT} -> ALSA:${ALSA_DEV}" >&2

case "$MODE" in
  play)
    exec ffmpeg -hide_banner -loglevel warning -nostdin -y \
      -protocol_whitelist file,udp,rtp -i "$SDP_FILE" -f alsa "$ALSA_DEV"
    ;;
  wav)
    exec ffmpeg -hide_banner -loglevel warning -nostdin -y \
      -protocol_whitelist file,udp,rtp -i "$SDP_FILE" -f wav "$OUT"
    ;;
  pcm)
    exec ffmpeg -hide_banner -loglevel warning -nostdin -y \
      -protocol_whitelist file,udp,rtp -i "$SDP_FILE" \
      -ac "$CHANNELS" -ar "${AR:-16000}" -acodec pcm_s16le -f s16le "$OUT"
    ;;
esac