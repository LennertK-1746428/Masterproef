import time
import subprocess
import pyshark
import os

#  To check which attributes an object has
# print(dir(capture[0]))
# print(capture[0].sniff_time)
# print(capture[0].sniff_timestamp)
# print(datetime.fromtimestamp(float(capture[0].sniff_timestamp)))

# init live capture object
capture = pyshark.LiveCapture(interface="WiFi", bpf_filter="src host 192.168.0.145 and udp port 1194")

# sniff packets for specified amount of seconds
capture.sniff(timeout=10)
print(capture)
print("Finished sniffing..")
len_captured = len([p for p in capture._packets])
print(f"Finished sniffing.. {len_captured} packets captured")

for packet in capture:
    if not ('OPENVPN' in packet):
        continue
    try:
        print("oof")
    except Exception as e:
        print("foof")