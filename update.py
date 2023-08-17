import urequests
import hashlib
import os

def download_firmware():
    firmware_res = urequests.get("http://eya-solutions.com/firmware.bin")
    firmware_hash = urequests.get("http://eya-solutions.com/firmware.sha256")
    firmware = firmware_res.content
    hash = firmware_hash.content

    test = hashlib.sha256(firmware).hexdigest()
    if test != hash:
        return None
    
    return firmware

def download_script():
    script_res = urequests.get("http://eya-solutions.com/installer.py")
    script_hash = urequests.get("http://eya-solutions.com/installer.sha256")
    script = script_res.content
    hash = script_hash.content

    test = hashlib.sha256(script).hexdigest()
    if test != hash:
        return None
    
    return script

def save_script(script, name: str):
    with open(name, "wb") as f:
        f.write(script)
    