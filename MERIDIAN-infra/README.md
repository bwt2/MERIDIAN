# MERIDIAN Infra
Dockerfile for MediaMTX media server, hosts WebRTC server with WHIP/WHEP and automatically converts RTSP to WebRTC.

```bash
docker compose up
```

Note: Publishing uses `/whip` (producer). Playback uses `/whep` (viewer).

## Test
### Mock External Camera Stream
Using local `/dev/video0` camera device, broadcast RSTP to `rtsp://127.0.0.1:8554/external_cam` to be read by `/internal` page.
```bash
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0   -c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p -g 60   -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/external_cam
```

### Mock Internal Camera Stream
Using local `/dev/video0` camera device, broadcast RSTP to `rtsp://127.0.0.1:8554/internal_cam` to be read by `/external` page.
```bash
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0   -c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p -g 60   -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/internal_cam
```
