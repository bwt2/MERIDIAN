# MERIDIAN
Monorepo for all relevant MERIDIAN source code. 

## Install

```bash
cd MERIDIAN-infra
docker compose up -d
```

```bash
cd MERIDIAN-web
pnpm install
pnpm dev
```

To run the MERIDIAN voice detection + tracking:

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python3 main.py --source /dev/video0 --show

# "meridian wake", "meridian sleep"
# Press 'q' to quit video window
```

## Service Architecture

```mermaid
sequenceDiagram
  participant RPI as Rpi
  participant EL as External Laptop (Linux)
  participant IP as Internal Phone

  EL ->> IP: segmented video, audio (zoom)
  IP ->> EL: audio (zoom)
  EL ->> RPI: audio (ffmpeg)
  RPI ->> EL: video (ffmpeg, MediaMTX, WebRTC)
```