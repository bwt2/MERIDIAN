## System Dependencies

Install PortAudio library (required for sounddevice):

```bash
# Ubuntu
sudo apt-get install portaudio19-dev

# mac
brew install portaudio
```

## Installation

```bash
python3 -m venv venv # or use root venv
source venv/bin/activate
pip install -e ./MERIDIAN-voice
```

## Usage
Hardcoded model paths in the same directory.
```bash
python3 keyword_detector.py
```