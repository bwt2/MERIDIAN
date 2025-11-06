import cv2
import time

vcap = cv2.VideoCapture("udp://@:5555")

while(1):
    ret, frame = vcap.read()
    if not ret:
        time.sleep(0.01)
        continue
    cv2.imshow('VIDEO', frame)
    cv2.waitKey(1)