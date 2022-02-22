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
    DIR = sys.argv[2] 
except:
    print("Specify OS and DIR")
    exit(0)


# constants
MTU = 1500
plot_index = 1
PLOT_ROWS = 3  # 1 row for each browser type
PLOT_COLS = 3    # 1 col for each trace 


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
    plt.colorbar(c)
    plt.xlim(0, MTU)
    plt.ylim(0, MTU)
    plt.xlabel("Normalized arrival time")
    plt.ylabel("Packet size (bytes)")
    plt.set_cmap('binary')
    title = savePath.split('/')[-1].split('.')[0]
    plt.title(title)
    # plt.savefig(savePath)


def visualize_trace(inFile, outFile):
    # read capture file
    print(inFile)
    capture = pyshark.FileCapture(inFile)
    capture.set_debug()
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
    session_2d_histogram(np.array(timestamps, dtype=float), np.array(sizes, dtype=int), binSize=20, vmax=5, savePath=outFile, plot=True)


# specify dirs
traces_dir = os.path.join(os.getcwd(), OS + "/traces/" + DIR)
out_dir = os.path.join(os.getcwd(), OS + "/visualizations")

# figsize = (num traces per browser * 8, num browsers * 6)
plt.figure(figsize=(24,18))

# visualize every trace file 
filenames = os.listdir(traces_dir)
print(filenames)
filenames.append("chrome2.pcapng")

for filename in sorted(filenames):
    print(f"Handling {filename}")
    # get paths
    filePath = os.path.join(traces_dir, filename)
    outPath = os.path.join(out_dir, filename.split('.')[0] + ".png")
    # visualize trace
    visualize_trace(filePath, outPath)

plt.suptitle("Comparison")
plt.savefig(os.path.join(out_dir, f"{DIR}_firefox_chrome_edge_1500x1500_5.png"))
# plt.show()