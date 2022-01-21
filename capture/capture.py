import subprocess
import os
import time
from capture_config import *

# determine filter
filter = f"src host {IP} and udp port {SERVER_PORT}"  

# determine output files
outfile = os.path.join(os.getcwd(), f"traces/file_upload/{OS}_{BROWSER}.pcapng")

# start capturing
capture = subprocess.Popen(args=["tshark", "-i", IFACE, "-w", outfile, "-f", filter])
while capture.poll() is not None: # while proces not alive
    print("Waiting for capture to start..")
    time.sleep(1)

# keep capturing until a key is submitted
input("Capture started. Submit anything to stop capturing:\n")

# stop process
capture.terminate()
while capture.poll() is None: # while proces still alive
    print("Waiting for capturing to stop..")
    time.sleep(1)
print("Capturing stopped successfully")
