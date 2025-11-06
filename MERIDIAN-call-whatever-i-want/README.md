# MERIDIAN-call-whatever-i-want

## Installation

```bash
python3 -m venv venv # or use root venv
source venv/bin/activate
pip install -e ./MERIDIAN-call-whatever-i-want
```

## Usage

```python
from stepper_module import BipolarStepper

stepper = BipolarStepper(pwmPinA=12, dirPinA=13, pwmPinB=16, dirPinB=19, RPM=60)
stepper.rotate(steps=200)  # Rotate 200 steps
stepper.rotate(angle=90)   # Rotate 90 degrees
```

