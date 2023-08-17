"""
This file contains the Connect class, which represents a connection to the server.
The connection is made using a TCP socket.
Data will be encrypted using AES-256 if an AES key is provided.
"""

import socket
import json
import encryption as enc

class Connect:
    def __init__(self, ip: str, port: str):
        self._ip = ip
        self._port = port
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((ip, port))


    # Disconnect from the server
    def disconnect(self):
        self._server.close()


    # Format, (encrypt), and send data to the server
    def send(self, aes_key: bytes | None, data: dict):
        jsondata = json.dumps(data)
        bytedata = jsondata.encode("utf-8")

        if aes_key != None:
            encrypted = enc.encrypt(aes_key, bytedata)
            self._server.send(encrypted)
        else:
            self._server.send(bytedata)
            

    # Receive, (decrypt), and format data from the server
    def receive(self, aes_key: bytes) -> dict:
        data = self._server.recv(1024)

        data = enc.decrypt(aes_key, data)

        if data == None:
            return {}
        
        data = data.decode("utf-8")
        return json.loads(data)
    

    # Send raw bytes to the server
    def send_bytes(self, data: bytes):
        self._server.send(data)

    
    # Receive raw bytes from the server
    def receive_bytes(self) -> bytes:
        return self._server.recv(1024)
