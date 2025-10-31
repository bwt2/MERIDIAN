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
        MM["MediaMTX"]
        ym["Yolo Model"]
    end
    rpi0["Raspberry Pi Zero + Camera"]
    m["Stepper Motor"]
    id["Internal Device"]
end
ed["External device"]

ym -- "Commands" --> m
rpi0 -- "UDP<br>(video)" --> ym
rpi0 -- "UDP<br>(video)" --> MM
MM <-- "WebRTC<br>(video, audio)" --> ed
MM -- "WebRTC<br>(video, audio)" --> id
id -- "WebRTC<br>(audio)" --> MM
```