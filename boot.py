"""
This file contains the boot sequence for the sensor.
All variables defined here are global and can be accessed from any file.

If configuration values are not set, the on-board LED will blink indefinitely.
"""

import config
import board_led as led
import network
import machine
import ntptime
import radar_sensor as sensor


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

# Set time
# ntptime.settime()
startup_time = machine.RTC().now()

# Initialize sensor
config.sensor_model = sensor.init()
config.uc_id = machine.unique_id().decode('UTF-8')

# Generate UUID
mac1 = config.uc_id.replace(':','')
mac_num = int(mac1,16)

temp = mac_num  * 10112197115111108117116105111110 # multiplied by 'eyasolution' in ascii number
temp = str(hex(temp)).upper()

uuid = temp[2:].ljust(32,'0')
uuid = uuid[:12] + '4' + uuid[13:]
uuid = uuid[:16] + '8' + uuid[17:]
uuid = uuid
config.uc_id = uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]

sensor_data = {
    "id": config.uc_id,
    "model": config.sensor_model,
    "location": config.location
}
