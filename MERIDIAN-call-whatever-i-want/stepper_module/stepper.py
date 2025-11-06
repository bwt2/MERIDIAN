from gpiozero import OutputDevice
import time

_power = OutputDevice(8)
_gnd = OutputDevice(9)
_dir_pin = OutputDevice(25)
_step_pin = OutputDevice(10)
_ms1 = OutputDevice(24)
_ms2 = OutputDevice(22)
_en = OutputDevice(18)

STEPS_PER_MOVE = 50 * 4
STEP_DELAY_MS = int(60000/(2*200))/16


def setup():
    _power.on()
    _gnd.off()
    _dir_pin.off()
    _step_pin.on()
    _ms1.off()
    _ms2.off()
    _en.off()


def left(steps=STEPS_PER_MOVE):
    _dir_pin.on()
    _step(steps)


def right(steps=STEPS_PER_MOVE):
    _dir_pin.off()
    _step(steps)


def _step(steps):
    for _ in range(steps):
        time.sleep(STEP_DELAY_MS * 0.001)
        _step_pin.on()
        time.sleep(STEP_DELAY_MS * 0.001)
        _step_pin.off()