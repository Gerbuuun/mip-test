"""
This file contains the main loop for the sensor.
It will try to connect to the server, and if it succeeds, it will start reading data from the sensor and sending it to the server.
The on-board LED will blink if the sensor is connected to the server but the server has not yet responded.
If any errors occur, the sensor will restart.
"""

import config
import uasyncio
import machine
import radar_sensor as sensor
from connection import Connect
import board_led as led

buffer = []

def connect_to_SBC():
    try:
        c = Connect(config.server_ip, config.server_port)
        
        sensor_data = {
            "id": config.uc_id,
            "model": config.sensor_model,
            "location": config.location
        }

        c.send(None, sensor_data)
        response = c.receive(config.aes_key)

        if not response["success"]:
            led.blink(100) # Blink indefinitely

        return c
    except Exception:
        machine.soft_reset()


async def check_connections(connection: Connect):
    while True:
        if not len(buffer) == 0:
            connection.send(config.aes_key, buffer.pop())
        await uasyncio.sleep_ms(1)


async def read_results():
    while True:
        values = sensor.update()
        buffer.insert(0, values)
        await uasyncio.sleep_ms(500)


async def check_heartbeat(connection: Connect):
    while True:
        heartbeat = sensor.send_command(b'\x01', b'\x01', b'\x0F')
        connection.send(config.aes_key, {
            "id": config.uc_id,
            "heartbeat": heartbeat == b'\x0F',
            "uptime": 
        })
        await uasyncio.sleep_ms(600_000) # 10 minutes


cnx = connect_to_SBC()

if cnx == None:
    machine.soft_reset()
else:
    read = uasyncio.create_task(read_results())
    conn = uasyncio.create_task(check_connections(cnx))
    heartbeat = uasyncio.create_task(check_heartbeat(cnx))

    loop = uasyncio.get_event_loop()
    try:
        loop.run_forever()
    except:
        if cnx != None:
            cnx.disconnect()
        machine.soft_reset()
