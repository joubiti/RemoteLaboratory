from machine import Pin
import time

##example MicroPython file which blinks a LED at 1/10 of a second

p0= Pin(2, Pin.OUT)
while True:
    p0.on()
    time.sleep(0.1)
    p0.off()
    time.sleep(0.1)

