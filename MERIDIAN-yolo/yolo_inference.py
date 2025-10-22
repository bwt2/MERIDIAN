#!/usr/bin/env python3

import cv2
from ultralytics import YOLO
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run YOLOv8 inference on video stream')
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
        default=0.25,
    )
    parser.add_argument(
        '--show',
        action='store_true',
    )
    parser.add_argument(
        '--save',
        type=str,
        default=None,
    )

    args = parser.parse_args()

    model = YOLO(args.model)

    # OPen source
    print(f"Opening video source: {args.source}")
    cap = cv2.VideoCapture(args.source)

    if not cap.isOpened():
        print(f"Error: Could not open video source {args.source}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video properties: {width}x{height} @ {fps}fps")

    # Set up video writer 
    out = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(args.save, fourcc, fps, (width, height))
        print(f"Saving to: {args.save}")

    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to read frame")
                break

            # Inference
            results = model(frame, conf=args.conf, verbose=False)

            annotated_frame = results[0].plot()

            # Print detections
            detections = results[0].boxes
            if len(detections) > 0:
                print(f"Frame {frame_count}: {len(detections)} objects detected")
                for box in detections:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    print(f"  - {label}: {conf:.2f}")

            # Display if --show
            if args.show:
                cv2.imshow('YOLOv8 Inference', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("User quit")
                    break

            # Save 
            if out:
                out.write(annotated_frame)

            frame_count += 1

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        print(f"Processed {frame_count} frames")


if __name__ == '__main__':
    main()
