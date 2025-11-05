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
python3 main.py --video-source /dev/video0 --show

## If you have a file (audio and video can be seperate)
python3 main.py --video-source my-video.mp4 --audio-source my-video.mp4 --show

# "meridian wake", "meridian sleep"
# Press 'q' to quit video window
```

## Service Architecture

```mermaid
flowchart TD
subgraph MERIDIAN
    subgraph Raspberry Pi
        subgraph WebRTC Infra 
            MM["MediaMTX"]
        end
        ym["Yolo Model"]
    end
    rpi0["Raspberry Pi Zero"]
    m["Stepper Motor"]
    sm["Smartphone"]
end
ed["External device"]

ym -- "Commands" --> m
rpi0 -- "RTSP Camera Stream" --> ym
rpi0 -- "RTSP Camera Stream" --> MM
MM <-- "WebRTC" --> ed
MM <-- "WebRTC" --> sm
```