import cv2
from ultralytics import YOLO
import argparse
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class PersonDetection:
    """Detection data for a person in a frame"""
    offset: float  # horizontal offset % from center (-1 to 1 with 0 at middle)
    conf: float
    bbox: Tuple[int, int, int, int]
    frame_number: int


class PersonTracker:
    """
    API for tracking (largest person)/people in video streams and position relative to frame center.
    """

    def __init__(self, model: str = "yolov8n.pt", conf_threshold: float = 0.25):
        self.model = YOLO(model)
        self.conf_threshold = conf_threshold

    def track(self, source):
        """
        Generator that yields PersonDetection or None for each frame
        Tracks only the closest person (largest bounding box)
        """
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Could not open video source: {source}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
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

                # Filter for people only (class 0)
                people = [box for box in detections if int(box.cls[0]) == 0]

                if len(people) == 0:
                    yield None
                    frame_count += 1
                    continue

                # Find closest person (largest bounding box area)
                closest_person = max(people, key=lambda box: self._bbox_area(box))

                # Extract data
                x1, y1, x2, y2 = closest_person.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = float(closest_person.conf[0])

                # Calculate horizontal offset from center
                person_center_x = (x1 + x2) // 2
                offset = (person_center_x - frame_center_x) / (width / 2)

                yield PersonDetection(
                    offset=offset,
                    conf=conf,
                    bbox=(x1, y1, x2, y2),
                    frame_number=frame_count
                )

                frame_count += 1

        finally:
            cap.release()

    def _bbox_area(self, box):
        # For finding closest person
        coords = box.xyxy[0].cpu().numpy()
        return (coords[2] - coords[0]) * (coords[3] - coords[1])


def main():
    # old version for mic
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--source',
        type=str,
        default='/dev/video0',
    )
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.65,
    )
    parser.add_argument(
        '--show',
        action='store_true',
    )

    args = parser.parse_args()

    model = YOLO(args.model)

    # OPen source
    print(f"Opening video source: {args.source}")
    cap = cv2.VideoCapture(args.source)

    if not cap.isOpened():
        print(f"Could not open video source {args.source}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Vid props: {width}x{height} @ {fps}fps")


    frame_count = 0

    # Calculate frame center
    frame_center_x = width // 2

    warning_threshold = 0.25  # Warning if person is 25% away from center

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to read frame")
                break

            # Inference
            results = model(frame, conf=args.conf, verbose=False)

            annotated_frame = frame.copy()

            detections = results[0].boxes
            people_detected = []

            for box in detections:
                cls = int(box.cls[0])
                if cls == 0:  # Person class
                    people_detected.append(box)

            # Process each person detection
            warnings = []
            for box in people_detected:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = float(box.conf[0])

                # Calculate person's center
                person_center_x = (x1 + x2) // 2

                # Calculate offset from frame center
                offset = (person_center_x - frame_center_x) / (width / 2)

                # Determine color based on offset
                # Green (center) -> Yellow (mid) -> Red (far)
                if abs(offset) < 0.2:  # Center zone
                    color = (0, 255, 0)  # Green 
                    position = "CENTER"
                elif abs(offset) < warning_threshold:  # Mid zone
                    color = (0, 255, 255)  # Yellow
                    position = "LEFT" if offset < 0 else "RIGHT"
                else:  # Far zone
                    color = (0, 0, 255)  # Red
                    position = "FAR LEFT" if offset < 0 else "FAR RIGHT"
                    warnings.append(f"Person too far {position}!")

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                label = f"Person {conf:.2f} | {position}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_size[1] - 10),
                    (x1 + label_size[0], y1),
                    color,
                    -1
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )

                # Centre line of person for reference 
                cv2.line(
                    annotated_frame,
                    (person_center_x, y1),
                    (person_center_x, y2),
                    color,
                    1
                )

            # Centre line of frame for reference
            cv2.line(
                annotated_frame,
                (frame_center_x, 0),
                (frame_center_x, height),
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

            if len(people_detected) > 0:
                print(f"Frame {frame_count}: {len(people_detected)} people detected")

            if args.show:
                cv2.imshow('YOLOv8 Person Tracking', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("User quit")
                    break

            frame_count += 1

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Processed {frame_count} frames")


if __name__ == '__main__':
    main()