from machine import UART
from micropython import const
import radar_response as r
import select

MAX_ATTEMPTS = const(5)

FRAME_START = const(b'\x53\x59')
FRAME_END = const(b'\x54\x43')

uart: UART
model = b''
failed_attempts = 0


class RadarTimeoutException(Exception):
    pass

class RadarPackageException(Exception):
    pass

class RadarNotResponding(Exception):
    pass


# Read a data frame from the sensor
# If the sensor does not respond, throw an exception
# If the sensor responds with an invalid frame, throw an exception
def _read():
  global uart
  poll = select.poll()
  poll.register(uart, select.POLLIN)
  while poll.poll(10000):
    # Check for header bytes
    # Done in two steps to prevent missing a frame start
    if uart.read(1) == b'\x53' and uart.read(1) == b'\x59':
        try:
          control = uart.read(1)
          command = uart.read(1)
          length = uart.read(2)
          data = uart.read(int.from_bytes(length, "big"))
          checksum = uart.read(1)
          endFrame = uart.read(2)
        except:
          raise RadarPackageException("Error while reading packet")

        # Check for end frame
        if endFrame != FRAME_END:
          raise RadarPackageException("Data frame not closed")

        # Calculate checksum and return data if checksum is correct
        frame = FRAME_START + control + command + length + data
        if (sum(frame).to_bytes(1, "big")) == checksum:
          return control, command, data
        else:
          raise RadarPackageException("Checksum failed")
  raise RadarTimeoutException("Sensor timeout")


# Write a data frame to the sensor
def _write(control: bytes, command: bytes, data: bytes):
  global uart
  length = len(data).to_bytes(2, "big")
  checksum = sum(FRAME_START + control + command + length + data).to_bytes(1, "big")

  uart.write(FRAME_START + control + command + length + data + checksum + FRAME_END)
  uart.flush()


# Send a reset command to the sensor
# Throw an exception if the sensor does not respond
def _reset():
  global uart, failed_attempts
  control = b'\x01'
  command = b'\x02'
  data = b'\x0F'

  _write(control, command, data)
  
  failed_attempts = 0
  ctrl, cmd, d = None, None, None

  # Read until the sensor responds with a reset response
  # If the sensor does not respond, throw an exception
  while ctrl != control or cmd != command or d != data:
    try:
      ctrl, cmd, d = _read()
      failed_attempts += 1
    except:
      failed_attempts += 1
      if failed_attempts > MAX_ATTEMPTS:
        raise RadarNotResponding("Sensor is not responding")
  failed_attempts = 0


# Get model info from the sensor
# If the sensor does not respond, reset the sensor and try again
def send_command(control: bytes, command: bytes, data: bytes):
  global uart, failed_attempts

  _write(control, command, data)

  reads = 0
  ctrl, cmd, d = _read()

  # Read until the sensor responds with the requested data
  # If the sensor does not respond, reset the sensor and try again
  while ctrl != control or cmd != command:
    try:
      ctrl, cmd, d = _read()

      reads += 1
      failed_attempts = 0

      # Response frame has probably passed already
      # Retry to get the sensor id
      if reads > 2:
        return send_command(control, command, data)
    except:
      failed_attempts += 1
      if failed_attempts > MAX_ATTEMPTS:
        _reset()
        return send_command(control, command, data)
  return d


# Read data from the sensor
def update():
    data = {}
    if model == b'R60A\x00':
        d = send_command(r.PRESENCE, r.EXISTENCE_STATUS, r.NO_DATA)
        data.update(r.format_data(r.PRESENCE, r.EXISTENCE_STATUS, d))
        d = send_command(r.HEART, r.HEART_RATE, r.NO_DATA)
        data.update(r.format_data(r.HEART, r.HEART_RATE, d))
        d = send_command(r.RESPIRATORY, r.RESPIRATORY_RATE, r.NO_DATA)
        data.update(r.format_data(r.RESPIRATORY, r.RESPIRATORY_RATE, d))
    elif model == b'R24D':
        d = send_command(r.PRESENCE, r.EXISTENCE_STATUS, r.NO_DATA)
        data.update(r.format_data(r.PRESENCE, r.EXISTENCE_STATUS, d))
    return data


# Setup the UART pins and reset the sensor
# Retrieve the sensor id
def init() -> dict:
  global uart, model
  uart = UART(1, baudrate=115200, bits=8, parity=None, stop=1, tx=4, rx=5)
  uart.init(timeout=10000)

  _reset()

  model = send_command(r.PRODUCT_INFO, r.HARDWARE_MODEL, r.NO_DATA)
  
  if model == b'R60A\x00': # MR60BHA1
      send_command(r.PRESENCE, r.TOGGLE_PRESENCE_MONITORING, r.TURN_OFF)
      send_command(r.HEART, r.TOGGLE_HEART_MONITORING, r.TURN_OFF)
      send_command(r.RESPIRATORY, r.TOGGLE_RESPIRATORY_MONITORING, r.TURN_ON)
      send_command(r.SLEEP, r.TOGGLE_SLEEP_MONITORING, r.TURN_OFF)
      send_command(b'\x84', b'\x0F', b'\x00')
  elif model == b'R24D': # MR24HPC1
      send_command(r.UNDERLYING_OPEN_FUNCTION, r.TOGGLE_UNDERLYING_OPEN_FUNCTION, r.TURN_ON)
      send_command(r.PRESENCE, r.SET_EXISTENCE_TIME, b'\x00')
  
  return model
  
