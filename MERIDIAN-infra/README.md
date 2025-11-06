# MERIDIAN Infra
Source files for infrastructure needed to be run in RPI and external laptop.

## External Device
To be run on the external device.
1. Bash script to grab audio capture device streaming from zoom and publish as RTP.

    ```bash
    cd external-device    
    PI_IP=192.168.0.22 PORT=5004 MONITOR=$(./select-audio-monitor.sh) ./rtp-audio-broadcaster.sh
    ```

### Test
Broadcast current audio.
```bash
cd external-device    
PI_IP=0.0.0.0 PORT=5004 MONITOR=$(./select-audio-monitor.sh) ./rtp-audio-broadcaster.sh
```

Listen to audio from rtp endpoint.
```bash
cd rpi
PORT=5004 MODE=play ./rtp-audio-listener.sh
```

## RPI
To be run on the raspberry PI.

1. Converts UDP stream to WebRTC for `MERIDIAN-web` WebRTC client to be run on external device.
    ```bash
    cd rpi
    docker compose up
    ```
    Dockerfile for MediaMTX media server, hosts WebRTC server with WHIP/WHEP and automatically converts RTP to WebRTC. 

2. Pipe audio from external device RTP broadcast to running python program:
    ```bash
    cd rpi
    PORT=5004 MODE=wav ./rtp-audio-listener.sh | python3 process_wav.py
    ```
    Alternatively, for testing purposes:
    ```bash
    cd rpi
    PORT=5004 MODE=play ./rtp-audio-listener.sh
    ```
    Note: Publishing uses `/whip` (producer). Playback uses `/whep` (viewer).

### Test
First, broadcast sine wave tone to rtp endpoint.
```bash
ffmpeg -re -f lavfi -i "sine=frequency=440:sample_rate=48000"   -ac 1 -c:a libopus -b:a 64k   -f rtp rtp://127.0.0.1:5004
```
Listen to sine wave from rtp endpoint.
```bash
cd rpi
PORT=5004 MODE=play ./rtp-audio-listener.sh
```