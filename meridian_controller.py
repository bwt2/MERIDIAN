import threading
from queue import Queue
from typing import Optional
import cv2
import time

from yolo_module import PersonTracker, PersonDetection
from voice_module import KeywordDetector, WakeWordDetection


class MeridianController:
    """
    Integrates YOLO tracking and voice detection
    """

    def __init__(
        self,
        video_source: str = "/dev/video0",
        yolo_model: str = "yolov8n.pt",
        yolo_confidence: float = 0.65,
        voice_confidence: float = 0.5,
        show: bool = False
    ):
        self.video_source = video_source
        self.show = show
        self.tracking_enabled = False
        # NOTE this is not the queue for frames (ie if yolo is too slow). it's a backlog for stepper motor
        self.detection_queue: Queue[Optional[PersonDetection]] = Queue(maxsize=10)
        self.shutdown_flag = threading.Event()

        self.person_tracker = PersonTracker(
            model=yolo_model,
            conf_threshold=yolo_confidence
        )
        self.keyword_detector = KeywordDetector(
            confidence_threshold=voice_confidence
        )

    def handle_wake_word(self, detection: WakeWordDetection):
        print(f"Detected: {detection.wake_word} {detection.confidence:.2f}")

        if "wake" in detection.wake_word.lower():
            self.tracking_enabled = True
            print("Tracking enabled")
        elif "sleep" in detection.wake_word.lower():
            self.tracking_enabled = False
            print("Tracking disabled")

    def voice_listener_thread(self):
        print("Starting voice monitoring")
        try:
            for detection in self.keyword_detector.listen():
                if self.shutdown_flag.is_set():
                    break
                self.handle_wake_word(detection)
        except Exception as e:
            if not self.shutdown_flag.is_set():
                print(f"Error: {e}")
        finally:
            print("voice detection stopped")

    def tracking_thread(self):
        print("Starting tracking")
        frame_count = 0

        for result in self.person_tracker.track(self.video_source, show_frame=self.show):
            frame_count += 1

            if self.show:
                frame, detection = result
            else:
                detection = result
                frame = None

            if detection is None:
                if frame_count % 30 == 0: # output to terminal readings every 30 frames so each second assuming 30fps for debuggingj
                    print(f"Frame {frame_count}: No person detected")

                if self.show and frame is not None:
                    cv2.imshow('MERIDIAN Tracking', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.shutdown_flag.set()
                        break

                if self.shutdown_flag.is_set():
                    break
                continue

            if self.tracking_enabled:
                offset_percent = detection.offset * 100
                direction = "CENTER"
                if detection.offset < -0.2:
                    direction = "LEFT"
                elif detection.offset > 0.2:
                    direction = "RIGHT"

                print(f"Frame {frame_count}: Offset {offset_percent:+.1f}% " # signed
                      f"({direction}, conf: {detection.conf:.2f})")

                ####################################################

                # TODO: Send tracking commands to stepper motor
                # Consume the detection queue

                ####################################################

            # Con
            if not self.detection_queue.full():
                self.detection_queue.put(detection)

            if self.show and frame is not None:
                cv2.imshow('MERIDIAN - Person Tracking', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.shutdown_flag.set()
                    break

            # Check shutdown flag
            if self.shutdown_flag.is_set():
                break

    def run(self):
        voice_thread = threading.Thread(
            target=self.voice_listener_thread,
            daemon=True
        )
        voice_thread.start()

        # Run tracking in main thread (blocking)
        try:
            self.tracking_thread()
        except KeyboardInterrupt:
            self.shutdown_flag.set()
        finally:
            # Kill threads
            self.shutdown_flag.set()

            if self.show:
                cv2.destroyAllWindows()

            # Wait for cleanup proper
            time.sleep(0.5)
