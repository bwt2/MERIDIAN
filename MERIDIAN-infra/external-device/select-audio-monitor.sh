#!/usr/bin/env bash
set -euo pipefail

# Read from the terminal even when invoked inside $( ... )
exec < /dev/tty

mapfile -t MONITORS < <(pactl list sources short | awk '/monitor/ {print $2}')
(( ${#MONITORS[@]} )) || { echo "No monitor sources found." >&2; exit 1; }

echo "Select a monitor source:" >&2
PS3="> "

select SEL in "${MONITORS[@]}" "Quit"; do
  if [[ "$REPLY" -ge 1 && "$REPLY" -le ${#MONITORS[@]} ]]; then
    printf '%s\n' "$SEL"     # <-- stdout (captured into MONITOR)
    break
  elif [[ "$SEL" == "Quit" ]]; then
    exit 1
  else
    echo "Invalid selection." >&2
  fi
done
