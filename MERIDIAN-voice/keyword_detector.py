#!/usr/bin/env python3

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
from openwakeword import utils
import os

CHUNK_SIZE = 1280
CHANNELS = 1
RATE = 16000

def main():
    utils.download_models()

    custom_models = ["meridian_wake.onnx", "meridian_sleep.onnx"]

    existing_models = [m for m in custom_models if os.path.exists(m)]

    if existing_models:
        print(f"Loading custom models: {existing_models}")
        model = Model(
            wakeword_models=existing_models,
            inference_framework="onnx"
        )
    else:
        print(f"No custom models found in current directory")
        model = Model(inference_framework="onnx")

    try:
        # Open audio stream using sounddevice
        with sd.InputStream(
            samplerate=RATE,
            channels=CHANNELS,
            dtype=np.int16,
            blocksize=CHUNK_SIZE
        ) as stream:
            while True:
                # Read audio 
                audio_data, overflowed = stream.read(CHUNK_SIZE)
                audio_data = audio_data.flatten().astype(np.int16)

                # Get predictions
                predictions = model.predict(audio_data)

                # Check for detections
                for wake_word, score in predictions.items():
                    if score > 0.5:  # conf
                        print(f"Detected: {wake_word} (confidence: {score:.2f})")

    except KeyboardInterrupt:
        print("\n\nterminating.")

    finally:
        print("Audio stream closed.")

if __name__ == "__main__":
    main()
