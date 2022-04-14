from numpy.core.fromnumeric import size
import pyshark
import sys
import os
import numpy as np
import matplotlib.pyplot as plt 
from datetime import datetime


# Handling CLI arguments #

try:
    DIR = sys.argv[1]
    TRAFFIC = sys.argv[2]
except:
    print("Specify DIR and Traffic type")
    exit(0)


# constants
MTU = 1500
plot_index = 1
PLOT_ROWS = 1  # 1 row for each os
PLOT_COLS = 3  # 1 col for each browser 


def processTimestamps(timestamps):
    # Convert timestamp is millis since first packet of the trace
    timestamps = np.array(timestamps) - timestamps[0]

    # Convert timestamps to range [0, MTU]
    timestamps = (timestamps / timestamps[-1]) * MTU

    return timestamps


# plot 2D histogram
def session_2d_histogram(timestamps, sizes, binSize, vmax, savePath, plot=False):
    global plot_index
    print(timestamps[:5])
    print(sizes[:5])
    
    H, xedges, yedges = np.histogram2d(sizes, timestamps, bins=(range(0, MTU + 1, binSize), range(0, MTU + 1, binSize)))
    
    # create new subplot
    plt.subplot(PLOT_ROWS, PLOT_COLS, plot_index)
    plot_index += 1
    
    # fill subplot
    c = plt.pcolormesh(xedges, yedges, H, vmax=vmax)
    #plt.colorbar(c)
    plt.xlim(0, MTU)
    plt.ylim(0, MTU)
    plt.xlabel("Normalized arrival time")
    plt.ylabel("Packet size (bytes)")
    plt.set_cmap('binary')
    title = f"Google Chrome"
    if "edge" in savePath:
        title = f"Microsoft Edge"
    elif "firefox" in savePath:
        title = f"Mozilla Firefox"
    plt.title(title)
    # plt.savefig(savePath)


def visualize_trace(inFile, outFile):
    # read capture file
    capture = pyshark.FileCapture(inFile)
    #capture.set_debug()
    # get timestamps and sizes
    timestamps = []
    sizes = []
    for packet in capture:
        if not ('OPENVPN' in packet):
            continue
        try:
            sizes.append(int(packet.openvpn.data.size))
            timestamps.append(float(packet.sniff_timestamp))
        except Exception as e:
            pass
    
    capture.close()

    # process timestamps
    timestamps = processTimestamps(timestamps)
    
    # create 2d hist and save
    session_2d_histogram(np.array(timestamps, dtype=float), np.array(sizes, dtype=int), binSize=20, vmax=5, savePath=inFile, plot=True)


# specify dirs
traces_windows_dir = os.path.join(os.getcwd(), "windows/traces/" + DIR)
traces_linux_dir = os.path.join(os.getcwd(), "linux/traces/" + DIR)
out_dir = os.getcwd()

# figsize = (num traces per os * 8, num os * 6)
plt.figure(figsize=(18,4))

# visualize every trace file 
filenames = []
for browser in ["chrome", "edge", "firefox"]:
    filenames.append(os.path.join(traces_windows_dir, browser + "2.pcapng"))
    #filenames.append(os.path.join(traces_linux_dir, browser + "2.pcapng"))
print(filenames)

for filename in sorted(filenames):
    print(f"Handling {filename}")

    # visualize trace
    visualize_trace(filename, "")

# plt.suptitle("Comparison of web browsers and operating systems")
plt.savefig(os.path.join(out_dir, "flowpic_windows_yt.png"), bbox_inches='tight')
# plt.show()