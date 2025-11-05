import argparse
from meridian_controller import MeridianController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=str,
        default="/dev/video0",
        help="webcam = /dev/video0, RTSP URL, or file path of mp4"
    )
    parser.add_argument(
        "--yolo-model",
        type=str,
        default="yolov8n.pt",
        help="model path"
    )
    parser.add_argument(
        "--yolo-conf",
        type=float,
        default=0.5,
        help="confidence"
    )
    parser.add_argument(
        "--voice-conf",
        type=float,
        default=0.5,
        help="voice conf"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="display cv2 window for debugging"
    )

    args = parser.parse_args()

    controller = MeridianController(
        video_source=args.source,
        yolo_model=args.yolo_model,
        yolo_confidence=args.yolo_conf,
        voice_confidence=args.voice_conf,
        show=args.show
    )

    controller.run()


if __name__ == "__main__":
    main()