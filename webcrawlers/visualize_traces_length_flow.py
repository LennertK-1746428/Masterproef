from numpy.core.fromnumeric import size
import pyshark
import sys
import os
import numpy as np
import matplotlib.pyplot as plt 

# constants
OS = "windows"
MTU = 1500


def processTimestamps(timestamps):
    # Convert timestamp is millis since first packet of the trace
    timestamps = np.array(timestamps) - timestamps[0]
    return timestamps


def visualize_trace(inFile, outFile):
    # read capture file
    capture = pyshark.FileCapture(inFile)
    
    # get timestamps and sizes
    timestamps = []
    sizes = []
    for packet in capture:
        if not ('OPENVPN' in packet):
            continue
        sizes.append(int(packet.openvpn.data.size))
        timestamps.append(float(packet.sniff_timestamp))
    
    # process timestamps
    timestamps = processTimestamps(timestamps)
    
    # plot
    # plt.plot(x, y, fmt) --> fmt = '[marker][line][color]'
    plt.figure(figsize=(100, 30))
    plt.scatter(timestamps, sizes)
    plt.ylim(0, MTU)
    plt.xlabel("Arrival time")
    plt.ylabel("Packet size (bytes)")
    plt.savefig(outFile)
    plt.clf()

    # close capture file
    capture.close()


# specify dirs
traces_dir = os.path.join(os.getcwd(), OS + "/traces/browsing")
out_dir = os.path.join(os.getcwd(), "visualization/browsing")

# visualize every trace file 
filenames = os.listdir(traces_dir)
for filename in sorted(filenames):
    # get paths
    filePath = os.path.join(traces_dir, filename)
    outPath = os.path.join(out_dir, OS + "_browsing_length_flow_" + filename.split('.')[0] + ".png")
    # visualize trace
    visualize_trace(filePath, outPath)
    exit(0)
