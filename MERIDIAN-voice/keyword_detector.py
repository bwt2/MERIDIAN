import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from openwakeword import utils
import os
from typing import Generator
from dataclasses import dataclass
from datetime import datetime

CHUNK_SIZE = 1280
CHANNELS = 1
RATE = 16000

@dataclass
class WakeWordDetection:
    wake_word: str
    confidence: float
    timestamp: datetime

class KeywordDetector:
    """
    Generator that you pass a callback fn to or just consume directly

        def my_callback(detection):
            print(f"Got {detection.wake_word}!")

        detector = KeywordDetector()
        detector.listen_with_callback(my_callback)
    """

    def __init__(
        self,
        custom_models: list = ["meridian_wake.onnx", "meridian_sleep.onnx"],
        confidence_threshold: float = 0.5,
        chunk_size: int = CHUNK_SIZE,
        sample_rate: int = RATE
    ):
        """
        Args:
            custom_models: List of custom model filepaths
            confidence_threshold: conf to trigger the callback
            chunk_size: Audio chunk size in samples
            sample_rate: Audio sample rate in Hz
        """
        self.confidence_threshold = confidence_threshold
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.custome_models = custom_models

        existing_models = [m for m in custom_models if os.path.exists(m)]

        if existing_models:
            print(f"Loading models: {existing_models}")
            self.model = Model(
                wakeword_models=existing_models,
                inference_framework="onnx"
            )
        else:
            print(f"No custom models found")
            return

    def listen(self) -> Generator[WakeWordDetection, None, None]:
        """
        Generator mode
        """
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=CHANNELS,
                dtype=np.int16,
                blocksize=self.chunk_size
            ) as stream:
                print("Listening..")
                
                while True:
                    audio_data, overflowed = stream.read(self.chunk_size)
                    if overflowed:
                        print("Buffer Overflow")

                    audio_data = audio_data.flatten().astype(np.int16)

                    # Inference
                    predictions = self.model.predict(audio_data)

                    # Yield detections 
                    for wake_word, score in predictions.items():
                        if score > self.confidence_threshold:
                            yield WakeWordDetection(
                                wake_word=wake_word,
                                confidence=score,
                                timestamp=datetime.now()
                            )

        except KeyboardInterrupt:
            print("\nExiting")
        finally:
            print("Fin")

    def listen_with_callback(self, callback,stop_condition) -> None:
        for detection in self.listen():
            callback(detection)
            if stop_condition and stop_condition(detection):
                break

def main():
    """Example with generator"""
    detector = KeywordDetector(confidence_threshold=0.5)

    for detection in detector.listen():
        print(f"Detected: {detection.wake_word} (conf: {detection.confidence:.2f}) at {detection.timestamp.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
