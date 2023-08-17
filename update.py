import urequests
import hashlib
import mip
import config
from esp32 import Partition

def download_firmware():
    for p in Partition.find(Partition.TYPE_APP):
        print(p)
    
    
    firmware_res = urequests.get("http://eya-solutions.com/firmware.bin")
    firmware_hash = urequests.get("http://eya-solutions.com/firmware.sha256")
    firmware = firmware_res.content
    hash = firmware_hash.content

    test = hashlib.sha256(firmware).hexdigest()
    if test != hash:
        return None
    
    return firmware

def install_modules():
    try:
        mip.install(f"http://{config.server_ip}")
    except Exception as e:
        print(e)

