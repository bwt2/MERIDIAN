# MERIDIAN-YOLO

YOLOv8 person tracking with position detection for MERIDIAN video streams.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

For integration (eg stepper motor control):

```python
from yolo_inference import PersonTracker

tracker = PersonTracker(conf_threshold=0.5)

for detection in tracker.track("video.mp4"):
    if detection:
        print(f"Offset: {detection.offset:.2f}")
        print(f"Confidence: {detection.confidence:.2f}")
        print(f"BBox: {detection.bbox}")

        # Control logic
        if abs(detection.offset) > 0.3:
            print("Person too far")
    else:
        print("No person detected")
```