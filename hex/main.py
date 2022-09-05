from machine import Pin
import time


p0= Pin(2, Pin.OUT)
while True:
    p0.on()
    time.sleep(0.1)
    p0.off()
    time.sleep(0.1)

