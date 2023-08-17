"""
This file contains the boot sequence for the sensor.
All variables defined here are global and can be accessed from any file.

If configuration values are not set, the on-board LED will blink indefinitely.
"""

import config
import board_led as led
import network
import ntptime
import radar_sensor as sensor
from machine import unique_id
from ubinascii import hexlify


# Check configuration
if config.ssid == None or config.password == None or config.aes_key == None or config.location == None or config.server_ip == None or config.server_port == None:
    led.blink(100) # Blink indefinitely

# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    wlan.connect(config.ssid, config.password)
    while not wlan.isconnected():
        machine.idle()

# Set time using private host
#ntptime.host = "www.eyasolutions.com"
ntptime.settime()

# Initialize sensor
config.sensor_model = sensor.init()

# Generate UUID
temp = hexlify(unique_id())
temp = int(temp,16)
temp = temp  * 10112197115111108117116105111110 # multiplied by 'eyasolution' in ascii number
temp = str(hex(temp)).upper()

uuid = temp[2:] + '0' * max(0, 32 - len(temp[2:])) # ljust is not available in micropython
uuid = uuid[:12] + '4' + uuid[13:]
uuid = uuid[:16] + '8' + uuid[17:]
config.uc_id = uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]

sensor_data = {
    "id": config.uc_id,
    "model": config.sensor_model,
    "location": config.location
}
