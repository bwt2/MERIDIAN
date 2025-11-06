# MERIDIAN Website
## About
WebRTC client / server. Requires `MERIDIAN-infra` RPI setup (MediaMTX dockerfile) for WebRTC connection. 

## Installation
Installation:
- Using `pnpm`

    ```bash
    corepack enable
    pnpm install
    pnpm dev
    ```
- Using `npm`

    ```bash
    npm install
    npm dev
    ```
    
### Test
Mock external camera stream using local `/dev/video0` camera device, broadcast RSTP to `rtsp://127.0.0.1:8554/external_cam` to be read by `/internal` page.
```bash
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0   -c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p -g 60   -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/external_cam
```