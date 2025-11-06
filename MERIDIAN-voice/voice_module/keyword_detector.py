import sounddevice as sd
import numpy as np
import openwakeword
from openwakeword.model import Model
from openwakeword import utils
import os
import stat
from typing import Generator, Union, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment

CHUNK_SIZE = 1280
CHANNELS = 1
RATE = 16000

@dataclass
class WakeWordDetection:
    wake_word: str
    confidence: float
    timestamp: datetime

class KeywordDetector:
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
        self.custom_models = custom_models

        openwakeword.utils.download_models()

        # Resolve model paths relative to package directory
        pkg_dir = Path(__file__).parent
        resolved_models = []
        for model in custom_models:
            # If path is relative, try package directory first
            if not os.path.isabs(model):
                pkg_model_path = pkg_dir / model
                if pkg_model_path.exists():
                    resolved_models.append(str(pkg_model_path))
                elif os.path.exists(model):
                    resolved_models.append(model)
            elif os.path.exists(model):
                resolved_models.append(model)

        existing_models = resolved_models

        if existing_models:
            print(f"Loading models: {existing_models}")
            self.model = Model(
                wakeword_models=existing_models,
                inference_framework="onnx"
            )
        else:
            print(f"No custom models found")
            return

    def _is_fifo(self, path):
        try:
            return stat.S_ISFIFO(os.stat(path).st_mode)
        except Exception:
            return False

    def _process_audio_from_file(self, file_path):
        """
        Process audio from mp4

        Args:
            file_path: Path to the audio/video file

        Yields:
            WakeWordDetection: Detection 
        """
        print(f"Loading audio from {file_path}...")

        audio = AudioSegment.from_file(file_path)

        # Convert to mono channel
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(self.sample_rate)
        audio = audio.set_sample_width(2)

        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)

        # Process chunkwise/discretise it
        num_chunks = len(samples) // self.chunk_size
        for i in range(num_chunks):
            start_idx = i * self.chunk_size
            end_idx = start_idx + self.chunk_size
            chunk = samples[start_idx:end_idx]

            # inference
            predictions = self.model.predict(chunk)

            for wake_word, score in predictions.items():
                if score > self.confidence_threshold:
                    timestamp_seconds = start_idx / self.sample_rate
                    yield WakeWordDetection(
                        wake_word=wake_word,
                        confidence=score,
                        timestamp=datetime.fromtimestamp(timestamp_seconds)  # Relative time
                    )

        print("File done")

    def _process_audio_from_stream(self, fifo_path):
        print(f"FIFO Detected!: {fifo_path}")

        try:
            with open(fifo_path, 'rb') as fifo:
                while True:
                    bytes_to_read = self.chunk_size * 2
                    chunk_bytes = fifo.read(bytes_to_read)

                    # EOF
                    if len(chunk_bytes) == 0:
                        print("FIFO closed (EOF)")
                        break

                    if len(chunk_bytes) < bytes_to_read:
                        continue

                    chunk = np.frombuffer(chunk_bytes, dtype=np.int16)

                    # inference
                    predictions = self.model.predict(chunk)

                    for wake_word, score in predictions.items():
                        if score > self.confidence_threshold:
                            yield WakeWordDetection(
                                wake_word=wake_word,
                                confidence=score,
                                timestamp=datetime.now()
                            )

        except Exception as e:
            print(f"Error")
        finally:
            print("FIFO DONE")

    def listen(self, source=None):
        if source is not None:
            if self._is_fifo(source):
                yield from self._process_audio_from_stream(str(source))
            else:
                # Regular file - load and process
                yield from self._process_audio_from_file(str(source))
            return

        # Otherwise use microphone
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

    def listen_with_callback(self, callback, stop_condition=None, source=None):
        for detection in self.listen(source=source):
            callback(detection)
            if stop_condition and stop_condition(detection):
                break