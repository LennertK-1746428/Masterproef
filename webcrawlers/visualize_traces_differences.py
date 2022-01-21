from numpy.core.fromnumeric import size
import pyshark
import sys
import os
import numpy as np
import matplotlib.pyplot as plt 
from datetime import datetime


# Handling CLI arguments #

try:
    OS = sys.argv[1] # "windows", "linux"
except:
    print("Specify 1 arguments: [1] = OS")
    exit(0)


# constants
MTU = 1500
plot_index = 1
PLOT_ROWS = 3   # 1 row for each browser type
PLOT_COLS = 6   # 1 col for each trace 


def processTimestamps(timestamps):
    # Convert timestamp is millis since first packet of the trace
    timestamps = np.array(timestamps) - timestamps[0]

    # Convert timestamps to range [0, MTU]
    timestamps = (timestamps / timestamps[-1]) * MTU

    return timestamps


# plot 2D histogram
def session_2d_histogram(timestamps, sizes, binSize, vmax, title, plot=False):
    global plot_index
    
    H, xedges, yedges = np.histogram2d(sizes, timestamps, bins=(range(0, MTU + 1, binSize), range(0, MTU + 1, binSize)))
    
    # create new subplot
    plt.subplot(PLOT_ROWS, PLOT_COLS, plot_index)
    plot_index += 1
    
    # fill subplot
    c = plt.pcolormesh(xedges, yedges, H, vmax=vmax)
    plt.colorbar(c)
    plt.xlim(0, MTU)
    plt.ylim(0, MTU)
    plt.xlabel("Normalized arrival time")
    plt.ylabel("Packet size (bytes)")
    plt.set_cmap('binary')
    plt.title(title)
    # plt.savefig(savePath)


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
    
    # create 2d hist and save
    title = inFile.split('/')[-2]
    session_2d_histogram(np.array(timestamps, dtype=float), np.array(sizes, dtype=int), binSize=20, vmax=5, title=title, plot=True)

    capture.close()


# specify dirs
traces_parent_dir = os.path.join(os.getcwd(), OS + "/traces")
out_dir = os.path.join(os.getcwd(), OS + "/visualizations")

# figsize = (num traces per browser * 8, num browsers * 6)
plt.figure(figsize=(PLOT_COLS * 8, PLOT_ROWS * 6))

# get all traces info
traces_dirs = os.listdir(traces_parent_dir)
traces_dirs = [d for d in traces_dirs if "browsing" in d] # only browsing 
traces_dirs.sort()
print(traces_dirs)
filenames = ["chrome1.pcapng", "edge1.pcapng", "firefox1.pcapng"]
for filename in filenames:
    for traces_dir in traces_dirs:
        filePath = os.path.join(traces_parent_dir, traces_dir, filename)
        print(filePath)
        # visualize trace
        visualize_trace(filePath, "")

plt.suptitle("Browsing comparison (visited site = www.uhasselt.be)")
plt.savefig(os.path.join(out_dir, "browsing_summary_firefox_chrome_edge_1500x1500_5.png"))
# plt.show()