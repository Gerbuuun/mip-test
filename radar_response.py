"""
This file contains functions that format the data received from the radar sensors:
 - Seeed Studios MR24HPC1 Radar Sensor
 - Seeed Studios MR60BHA1 Radar Sensor
 
The function 'format_data' will return one of these functions based on which control word is received.
Both sensors use the same control words and data formats, but some commands are only supported by one sensor.

These functions are based on the data found in the tables from:
 - Seeed Studios MR24HPC1 Radar Sensor Datasheet: https://files.seeedstudio.com/wiki/mmWave-radar/MR24HPC1_User_Manual-V1.5.pdf
 - Seeed Studios MR60BHA1 Radar Sensor Datasheet: https://files.seeedstudio.com/wiki/60GHzradar/new_res/MR60BHA1_user_manual-V1.9.pdf
Only a subset of the commands are implemented as the rest are not relevant for this project.
"""

from micropython import const

NO_DATA = const(b'\x0F')
TURN_ON = const(b'\x01')
TURN_OFF = const(b'\x00')

# Control Words
SYSTEM_FUNCTIONS = const(b'\x01')
PRODUCT_INFO = const(b'\x02')
OPERATION_STATUS = const(b'\x05')
DETECTION_RANGE = const(b'\x07')
UNDERLYING_OPEN_FUNCTION = const(b'\x08')
PRESENCE = const(b'\x80')
RESPIRATORY = const(b'\x81')
SLEEP = const(b'\x84')
HEART = const(b'\x85')

# System Functions
SYSTEM_HEARTBEAT = const(b'\x80')
SYSTEM_RESET = const(b'\x02')

# Product Info
PRODUCT_MODEL = const(b'\xA1')
PRODUCT_ID = const(b'\xA2')
HARDWARE_MODEL = const(b'\xA3')
FIRMWARE_VERSION = const(b'\xA4')

# Operation Status
INITIALIZATION = const(b'\x81')

# Detection Range
OUT_OF_BOUNDS = const(b'\x87')

# Underlying Open Function
TOGGLE_UNDERLYING_OPEN_FUNCTION = const(b'\x00')

# Presence
TOGGLE_PRESENCE_MONITORING = const(b'\x00')
SET_EXISTENCE_TIME = const(b'\x0A')
PRESENCE_STATUS = const(b'\x80')
EXISTENCE_STATUS = const(b'\x81')
MOVEMENT_STATUS = const(b'\x82')
MOVEMENT_ENERGY = const(b'\x83')
EXISTENCE_DISTANCE = const(b'\x84')

# Heart
TOGGLE_HEART_MONITORING = const(b'\x00')
HEART_MONITORING_STATUS = const(b'\x80')
HEART_RATE = const(b'\x82')
HEART_WAVEFORM = const(b'\x85')

# Respiratory
TOGGLE_RESPIRATORY_MONITORING = const(b'\x00')
RESPIRATORY_MONITORING_STATUS = const(b'\x80')
RESPIRATORY_SPEED = const(b'\x81')
RESPIRATORY_RATE = const(b'\x82')
RESPIRATORY_WAVEFORM = const(b'\x85')

# Sleep
TOGGLE_SLEEP_MONITORING = const(b'\x00')


def _handle_heart_rate_monitor(command: bytes, data: bytes) -> dict:
    return {
        b'\x00': lambda: { "heart_monitoring": data == b'\x01' },
        b'\x02': lambda: { "heart_rate": int.from_bytes(data, "big") },
        b'\x05': lambda: { "heart_waveform": [b for b in data] },
        b'\x82': lambda: { "heart_rate": int.from_bytes(data, "big") }
    }.get(command, lambda: { "error": "Invalid Heart Rate Monitoring Command: " + str(command) + " " + str(data) })()


def _handle_respiratory_monitor(command: bytes, data: bytes) -> dict:
    respiratory_speeds = ['Normal', 'Fast', 'Slow', 'None']
    return {
        b'\x00': lambda: { "respiratory_monitoring": data == b'\x01' },
        b'\x01': lambda: { "resporatory_speed": respiratory_speeds[int.from_bytes(data, "big")-1] },
        b'\x01': lambda: { "respiratory_rate": int.from_bytes(data, "big") },
        b'\x02': lambda: { "respiratory_waveform": [b for b in data] },
        b'\x82': lambda: { "respiratory_rate": int.from_bytes(data, "big") }
     }.get(command, lambda: { "error": "Invalid Respiratory Monitoring Command: " + str(command) + " " + str(data) })()


def _handle_sleep_monitor(command: bytes, data: bytes) -> dict:
    bed_status = ['Out Bed', 'In Bed', 'None']
    sleep_status = ['Deep Sleep', 'Light Sleep', 'Awake', 'None']
    return {
        b'\x00': lambda: { "sleep_monitoring": data == b'\x01' },
        b'\x01': lambda: { "bed_status": bed_status[int.from_bytes(data, "big")] },
        b'\x02': lambda: { "sleep_status": sleep_status[int.from_bytes(data, "big")] },
        b'\x03': lambda: { "awake_duration": int.from_bytes(data, "big") },
        b'\x04': lambda: { "light_sleep_duration": int.from_bytes(data, "big") },
        b'\x05': lambda: { "deep_sleep_duration": int.from_bytes(data, "big") },
    }.get(command, lambda: { "error": "Invalid Sleep Monitoring Command: " + str(command) + " " + str(data) })()


def _handle_human_presence(command: bytes, data: bytes) -> dict:
    movement_status = ['None', 'Stationary', 'Active']
    presence_times = ['None', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '60m']
    return {
        b'\x00': lambda: { "presence_monitoring": data == b'\x01' },
        b'\x01': lambda: { "existence_status": data == b'\x01' },
        b'\x02': lambda: { "movement_status": movement_status[int.from_bytes(data, "big")] },
        b'\x03': lambda: { "movement_energy": int.from_bytes(data, "big") },
        b'\x04': lambda: { "presence_distance": int.from_bytes(data, "big") },
        b'\x05': lambda: { "presence_orientation": int.from_bytes(data, "big") },
        b'\x0A': lambda: { "set_presence_time": presence_times[int.from_bytes(data, "big")] },
        b'\x81': lambda: { "existence_status": data == b'\x01' },
    }.get(command, lambda: { "error": "Invalid Presence Monitoring Command: " + str(command) + " " + str(data) })()


def _handle_radar_detection_range(command: bytes, data: bytes) -> dict:
    return {
        b'\x07': lambda: { "in_range": data == b'\x01' },
        b'\x87': lambda: { "in_range": data == b'\x01' },
    }.get(command, lambda: { "error": "Invalid Detection Range Command: " + str(command) + " " + str(data) })()


def _handle_product_info(command: bytes, data: bytes) -> dict:
    return {
        b'\xA1': lambda: { "model": data },
        b'\xA2': lambda: { "product_id": data },
        b'\xA3': lambda: { "hardware_model": data },
        b'\xA4': lambda: { "firmware_version": data },
    }.get(command, lambda: { "error": "Invalid Product Info Command: " + str(command) + " " + str(data) })()


def _handle_system_functions(command: bytes, data: bytes) -> dict:
    return {
        b'\x01': lambda: { "heartbeat": data == b'\x0F' },
        b'\x80': lambda: { "heartbeat": data == b'\x0F' },
        b'\x02': lambda: { "reset": data == b'\x0F' },
    }.get(command, lambda: { "error": "Invalid System Function Command: " + str(command) + " " + str(data) })()


def _handle_operation_status(command: bytes, data: bytes) -> dict:
    scene_settings = ['Not set', 'Living Room', 'Bedroom', 'Bathroom', 'Area Detection']
    sensitivity_settings = ['Not set', '2 meter', '3 meter', '4 meter']
    return {
        b'\x01': lambda: { "init_complete": data == b'\x01' },
        b'\x81': lambda: { "init_complete": data == b'\x01' },
        b'\x07': lambda: { "scene_settings": scene_settings[int.from_bytes(data, "big")] },
        b'\x87': lambda: { "scene_settings": scene_settings[int.from_bytes(data, "big")] },
        b'\x08': lambda: { "sensitivity_settings": sensitivity_settings[int.from_bytes(data, "big")] },
        b'\x88': lambda: { "sensitivity_settings": sensitivity_settings[int.from_bytes(data, "big")] },
    }.get(command, lambda: { "error": "Invalid Operation Status Command: " + str(command) + " " + str(data) })()


def _handle_underlying_open_function(command: bytes, data: bytes) -> dict:
    return {
        b'\x00': lambda: { 'underlying_open_function': data == b'\x01' },
        b'\x01': lambda: { 'underlying_values': [b for b in data] },
    }.get(command, lambda: { "error": "Invalid Underlying Open Function Command: " + str(command) + " " + str(data) })()


def format_data(control_word: bytes, command: bytes, data: bytes) -> dict:
    return {
        b'\x01': lambda: _handle_system_functions(command, data),
        b'\x02': lambda: _handle_product_info(command, data),
        b'\x05': lambda: _handle_operation_status(command, data),
        b'\x07': lambda: _handle_radar_detection_range(command, data),
        b'\x08': lambda: _handle_underlying_open_function(command, data),
        b'\x80': lambda: _handle_human_presence(command, data),
        b'\x81': lambda: _handle_respiratory_monitor(command, data),
        b'\x84': lambda: _handle_sleep_monitor(command, data),
        b'\x85': lambda: _handle_heart_rate_monitor(command, data)
    }.get(control_word, lambda: { "error": "Invalid Control Word" })()

