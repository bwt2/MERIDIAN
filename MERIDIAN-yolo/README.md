# MERIDIAN-YOLO

YOLOv8 inference for MERIDIAN video streams.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 yolo_inference.py --source /dev/video0 --show
```

### Read from RTSP stream
```bash
python3 yolo_inference.py --source rtsp://127.0.0.1:8554/meridian_cam --show
```