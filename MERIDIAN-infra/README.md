# MERIDIAN Infra
Dockerfile for MediaMTX media server, hosts WebRTC and converts FTSP to WebRTC.

## Test
Using local `/dev/video0` logitech c270 webcam, broadcast RSTP to `rtsp://127.0.0.1:8554/meridian_cam`.
```bash
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0   -c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p -g 60   -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/meridian_cam
```