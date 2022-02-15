from numpy.core.fromnumeric import size
import pyshark
import sys
import os
import numpy as np
import matplotlib.pyplot as plt 
from datetime import datetime


# Handling CLI arguments #

# try:
#     OS = sys.argv[1] # "windows", "linux"
#     DIR = sys.argv[2] 
# except:
#     print("Specify 2 arguments: [1] = OS, [2] = TRACES DIR")
#     exit(0)


# constants
MTU = 1500
plot_index = 1
PLOT_ROWS = 3  # 1 row for each browser type
PLOT_COLS = 1    # 1 col for each trace 


def processTimestamps(timestamps):
    # Convert timestamp is millis since first packet of the trace
    timestamps = np.array(timestamps) - timestamps[0]

    # Convert timestamps to range [0, MTU]
    timestamps = (timestamps / timestamps[-1]) * MTU

    return timestamps


# plot 2D histogram
def session_2d_histogram(timestamps, sizes, binSize, vmax, filename, plot=False):
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
    title = filename.split('\\')[-1].split('.')[0]
    plt.title(title)
    # plt.savefig(savePath)


def visualize_trace(inFile):
    # read capture file
    print(inFile)
    capture = pyshark.FileCapture(inFile)
    
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
    
    # process timestamps
    timestamps = processTimestamps(timestamps)
    
    # create 2d hist and save
    session_2d_histogram(np.array(timestamps, dtype=float), np.array(sizes, dtype=int), binSize=20, filename=inFile, vmax=5, plot=True)

    capture.close()


# specify dirs
#traces_dir = os.path.join(os.getcwd(), OS + "/traces/" + DIR)
#out_dir = os.path.join(os.getcwd(), OS + "/visualizations")
traces_dir = os.path.join(os.getcwd(), "fons")
out_dir = os.path.join(os.getcwd(), "fons")

# figsize = (num traces per browser * 8, num browsers * 6)
plt.figure(figsize=(8,18))

# visualize every trace file 
filenames = os.listdir(traces_dir)
filenames = [f for f in filenames if "vpn" in f and "windows" in f]

for filename in sorted(filenames):
    # get paths
    filePath = os.path.join(traces_dir, filename)

    # visualize trace
    visualize_trace(filePath)

plt.suptitle("Comparison")
outPath = os.path.join(out_dir, "vis2.png")
plt.savefig(outPath)
# plt.savefig(os.path.join(out_dir, DIR + "_firefox_chrome_edge_1500x1500_5.png"))
# plt.show()