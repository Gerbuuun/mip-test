"""
This module is used to control the on-board LED on the ESP32.
The radar LED is connected to pin 1.
The power LED is directly connected to the 5V pin.
"""

import time
from machine import Pin

led = Pin(1, Pin.OUT)


def blink(milliseconds: int):
  while True:
    led.on()
    time.sleep_ms(milliseconds)
    led.off()
    time.sleep_ms(milliseconds)
        
        
def on():
  led.on()
    

def off():
  led.off()
