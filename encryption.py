"""
This module provides functions for encrypting and decrypting data using AES-256.
Messages are encrypted using AES-256 in CBC mode to keep the encrypted data from having a pattern.
"""

from ucryptolib import aes
from uos import urandom

# Encrypt data and prepend IV
def encrypt(key: bytes, data: bytes) -> bytes:
    iv = urandom(16)
    cipher = aes(key, 2, iv) # 2 = CBC
    
    padded = data + b" " * (16 - len(data) % 16)
    encrypted = cipher.encrypt(padded)
    
    return iv + encrypted


# Extract IV from data, decrypt, and trim data
def decrypt(key: bytes, data: bytes) -> bytes | None:
    iv = data[0:16]
    encrypted = data[16:]
    cipher = aes(key, 2, iv) # 2 = CBC

    decrypted = cipher.decrypt(encrypted)
    if decrypted == None:
        return None
    
    return decrypted.rstrip(b" ")
    