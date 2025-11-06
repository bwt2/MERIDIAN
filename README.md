# MERIDIAN
Monorepo for all relevant MERIDIAN source code. 

## Install
### External Device
Broadcast audio to rtp for Rasberry PI.
```bash
cd MERIDIAN-infra/external-device    
PI_IP=10.74.130.118 PORT=5004 MONITOR=$(./select-audio-monitor.sh) ./rtp-audio-broadcaster.sh # insert actual PI_IP here
```
Connect to webRTC client:
```
http://<pi_ip>:5173
```

### Raspberry PI
### WebRTC Setup
Setup MediaMTX WebRTC server to get PI cam UDP -> WebRTC. On the RPI:

```bash
ssh <rpi-0> # ssh rpi-win-zero@10.42.0.2
rpicam-vid -t 0 -n --inline -o - | ffmpeg -hide_banner -loglevel warning -re -f h264 -i -   -rtsp_transport tcp   -c:v copy   -f rtsp rtsp://10.74.130.118:8554/internal_cam
```
```bash
cd MERIDIAN-infra/rpi
docker compose up -d
```
Set up WebRTC web client: 
```bash
# install npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 20
nvm use 20

cd MERIDIAN-web
npm install
npm run dev -- --host
```
### Voice Detection and Tracking Setup 
Setup rtp listener for MERIDIAN voice detection + tracking. For more details, see `MERIDIAN-infra`'s `README.md`.
```bash
# install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# setup rtp listener and  MERIDIAN voice detection + tracking
mkfifo /tmp/audio_pipe.pcm

python3 main.py --video-source rtsp://10.74.130.118:8554/internal_cam --audio-source /tmp/audio_pipe.pcm 

cd MERIDIAN-infra/rpi
PORT=5004 OUT=/tmp/audio_pipe.pcm AR=16000 CHANNELS=1 MODE=pcm ./rtp-audio-listener.sh 
```

#### Testing
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
sequenceDiagram
  participant RPI as Rpi
  participant EL as External Laptop (Linux)
  participant IP as Internal Phone

  EL ->> IP: segmented video, audio (zoom)
  IP ->> EL: audio (zoom)
  EL ->> RPI: audio (ffmpeg)
  RPI ->> EL: video (ffmpeg, MediaMTX, WebRTC)
```