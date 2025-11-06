from gpiozero import OutputDevice, LED
from signal import pause
import time


# credit to
# https://github.com/CoreElectronics/CE-Makerverse-Motor-Driver-2ch-MicroPython-Module/blob/main/Makerverse_Motor_2ch.py

class BipolarStepper():
    def __init__(self, pwmPinA = 0, dirPinA = 1, pwmPinB = 2, dirPinB = 3, RPM = 60, stepsPerRotation = 200):

        self.pwmA = OutputDevice(pwmPinA)
        self.pwmB = OutputDevice(pwmPinB)
        self.dirA = OutputDevice(dirPinA)
        self.dirB = OutputDevice(dirPinB)

        self.pwmA.on()
        self.pwmB.on()
        self.dirA.on()
        self.dirB.on()

        self.next = "A"

        self.steps = 0

        self.stepDelay_ms = int(60000/(RPM*stepsPerRotation))

        self.RPM = RPM
        self.stepsPerRotation = stepsPerRotation

    def setRPM(self, RPM):
        self.stepDelay_ms = int(60000/(RPM*self.stepsPerRotation))

    def setHome(self):
        self.steps = 0

    def returnHome(self):
        while self.steps > 0:
            self.backwardStep()
            time.sleep(self.stepDelay_ms * 0.001)
        while self.steps < 0:
            self.forwardStep()
            time.sleep(self.stepDelay_ms * 0.001)

    def getSteps(self):
        return self.steps

    def getAngle(self):
        return self.steps % self.stepsPerRotation / self.stepsPerRotation * 360

    def forwardStep(self):
        if self.next == "A":
            if self.dirA.value == 1:
                self.dirA.off()
            else:
                self.dirA.on()
            self.next = "B"
        else:
            if self.dirB.value == 1:
                self.dirB.off()
            else:
                self.dirB.on()
            self.next = "A"
        self.steps += 1

    def backwardStep(self):
        if self.next == "A":
            if self.dirB.value == 1:
                self.dirB.off()
            else:
                self.dirB.on()
            self.next = "B"
        else:
            if self.dirA.value == 1:
                self.dirA.off()
            else:
                self.dirA.on()
            self.next = "A"
        self.steps -= 1

    def rotate(self, steps = 0, angle = None):
        if angle is not None:
            steps = round(angle/360.0*self.stepsPerRotation)

        if steps < 0:
            while steps < 0:
                self.backwardStep()
                steps += 1
                time.sleep(self.stepDelay_ms * 0.001)
        else:
            while steps > 0:
                self.forwardStep()
                steps -= 1
                time.sleep(self.stepDelay_ms * 0.001)

# GPIO Pin Mapping:
# 19 -> DIR B
# 16 -> PWM B
# 13 -> DIR A
# 12 -> PWM A
