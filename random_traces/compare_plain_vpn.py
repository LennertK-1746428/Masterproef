import time
import subprocess
import pyshark
import os
from collections import Counter

OUT_FILE = open("diffcounts_vpn_plain.txt", "w")
DIR = "lennert"
files_dir = os.path.join(os.getcwd(), DIR)
files = os.listdir(files_dir)
# all (vpn, plain) tuples
files.sort()
files = [(f, f.replace("vpn", "plain")) for f in files if f.split('.')[-1] == "pcapng" and "vpn" in f]
print(files)


def find_first_mismatch(plain_capture, vpn_capture, expected_diff):
    
    # get lengths
    length_plain = len([p for p in plain_capture])
    length_vpn = len([p for p in vpn_capture])
    
    OUT_FILE.write("Looping forward and finding first mismatch..\n")

    # loop through both and notify when there is a mismatch (not 1:1)
    for i in range(length_plain):

        # get packet size 
        plain_packet_size = int(plain_capture[i].length)
        vpn_packet_size = int(vpn_capture[i].length) #.openvpn.data.size
        
        # calc diff and check if it is what we expect, else log the index
        diff = vpn_packet_size - plain_packet_size
        if diff != expected_diff:
            OUT_FILE.write(f"i: {i}, diff: {diff}\n")
            break

    OUT_FILE.write("Looping backward and finding first mismatch..\n")

    # loop backwards
    while length_plain > 0 and length_vpn > 0:

        length_plain -= 1
        length_vpn -= 1

        # get packet size 
        plain_packet_size = int(plain_capture[length_plain].length)
        vpn_packet_size = int(vpn_capture[length_vpn].length) #.openvpn.data.size

        # calc diff and check if it is what we expect, else log the index
        diff = vpn_packet_size - plain_packet_size
        if diff != expected_diff:
            OUT_FILE.write(f"plain: {length_plain}, vpn: {length_vpn}, diff: {diff}\n")
            break

    OUT_FILE.write("\n")


for f_tuple in files:

    OUT_FILE.write(f"Checking {f_tuple}\n")

    # get filepaths 
    plain_filepath = os.path.join(files_dir, f_tuple[1])
    vpn_filepath = os.path.join(files_dir, f_tuple[0])

    # read capture files
    plain_capture = pyshark.FileCapture(plain_filepath)
    vpn_capture = pyshark.FileCapture(vpn_filepath)
    
    ### find mismatches ###
    # expected_diff = 66 if "linux" in f_tuple[0] else 52
    # find_first_mismatch(plain_capture, vpn_capture, expected_diff)
    
    ### count size differences ###

    # get lengths
    length_plain = len([p for p in plain_capture])
    length_vpn = len([p for p in vpn_capture])
    OUT_FILE.write(f"VPN length: {length_vpn}, plain length: {length_plain}\n")

    diff_lst = []
    plain_lst = []
    vpn_lst = []
    # loop through both store difference
    for i in range(length_plain):
        if i >= length_vpn:
            break

        # get packet size 
        plain_packet_size = int(plain_capture[i].length)
        vpn_packet_size = int(vpn_capture[i].length) #.openvpn.data.size
        
        plain_lst.append(plain_packet_size)
        vpn_lst.append(vpn_packet_size)

        # calc diff and increase counter
        diff = vpn_packet_size - plain_packet_size
        diff_lst.append(diff)

    
    diff_counts = Counter(diff_lst)
    most_frequent = diff_counts.most_common(3)
    most_frequent = [(key, f"Count: {val} = {round((val/len(diff_lst))*100, 2)}%") for (key, val) in most_frequent]
    OUT_FILE.write(f"Differences: {most_frequent}\n")

    plain_counts = Counter(plain_lst)
    most_frequent = plain_counts.most_common(3)
    most_frequent = [(key, f"Count: {val} = {round((val/len(plain_lst))*100, 2)}%") for (key, val) in most_frequent]
    OUT_FILE.write(f"Plain: {most_frequent}\n")

    vpn_counts = Counter(vpn_lst)
    most_frequent = vpn_counts.most_common(3)
    most_frequent = [(key, f"Count: {val} = {round((val/len(vpn_lst))*100, 2)}%") for (key, val) in most_frequent]
    OUT_FILE.write(f"VPN: {most_frequent}\n\n")

    # clear everything with count < 5
    # diff_counts = dict(filter(lambda elem: elem[1] >= 5, diff_counts.items()))

    plain_capture.close()
    vpn_capture.close()

OUT_FILE.close()
