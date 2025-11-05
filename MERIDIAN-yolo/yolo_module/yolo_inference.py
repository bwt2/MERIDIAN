import cv2
from ultralytics import YOLO
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path
import os


@dataclass
class PersonDetection:
    offset: float  # horizontal offset % from center (-1 to 1 with 0 at middle)
    conf: float
    bbox: Tuple[int, int, int, int]
    frame_number: int


class PersonTracker:
    def __init__(self, model: str = "yolov8n.pt", conf_threshold: float = 0.25):
        # Get relative model path if abs not given
        if not os.path.isabs(model):
            pkg_dir = Path(__file__).parent
            pkg_model_path = pkg_dir / model
            if pkg_model_path.exists():
                model = str(pkg_model_path)

        self.model = YOLO(model)
        self.conf_threshold = conf_threshold

    def track(self, source, show_frame=False):
        """
        Generator that yields (frame, PersonDetection) or (frame, None) for each frame
        Tracks only the closest person (largest bounding box)
        """
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Could not open video source: {source}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_center_x = width // 2
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Run inference
                results = self.model(frame, conf=self.conf_threshold, verbose=False)
                detections = results[0].boxes

                # Create annotated frame if needed
                if show_frame:
                    annotated_frame = frame.copy()
                    # Draw center line
                    cv2.line(annotated_frame, (frame_center_x, 0),
                            (frame_center_x, height), (255, 255, 255), 1, cv2.LINE_AA)

                # Filter for people only (class 0)
                people = [box for box in detections if int(box.cls[0]) == 0]

                if len(people) == 0:
                    if show_frame:
                        yield (annotated_frame, None)
                    else:
                        yield None
                    frame_count += 1
                    continue

                # Find closest person (largest bounding box area)
                closest_person = max(people, key=lambda box: self._bbox_area(box))

                x1, y1, x2, y2 = closest_person.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = float(closest_person.conf[0])

                # Calculate horizontal offset from center
                person_center_x = (x1 + x2) // 2
                offset = (person_center_x - frame_center_x) / (width / 2)

                detection = PersonDetection(
                    offset=offset,
                    conf=conf,
                    bbox=(x1, y1, x2, y2),
                    frame_number=frame_count
                )

                if show_frame:
                    if abs(offset) < 0.2:
                        colour = (0, 255, 0)  # Green - centered
                        position = "CENTER"
                    elif abs(offset) < 0.5:
                        colour = (0, 255, 255)  # Yellow - mid
                        position = "LEFT" if offset < 0 else "RIGHT"
                    else:
                        colour = (0, 0, 255)  # Red - far
                        position = "FAR LEFT" if offset < 0 else "FAR RIGHT"

                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), colour, 2)

                    # Draw person center line
                    cv2.line(annotated_frame, (person_center_x, y1),
                            (person_center_x, y2), colour, 1)

                    # Draw label
                    label = f"Person {conf:.2f} | {position}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10),
                                (x1 + label_size[0], y1), colour, -1)
                    cv2.putText(annotated_frame, label, (x1, y1 - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    yield (annotated_frame, detection)
                else:
                    yield detection

                frame_count += 1

        finally:
            cap.release()
            if show_frame:
                cv2.destroyAllWindows()

    def _bbox_area(self, box):
        # For finding closest person
        coords = box.xyxy[0].cpu().numpy()
        return (coords[2] - coords[0]) * (coords[3] - coords[1])