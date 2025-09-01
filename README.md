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