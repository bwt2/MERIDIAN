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
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  

# Install dependencies
pip3 install -r requirements.txt
```

## Usage
Hardcoded model paths in the same directory.
```bash
python3 keyword_detector.py
```