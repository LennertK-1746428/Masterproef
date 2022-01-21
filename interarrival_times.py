from numpy.core.fromnumeric import size
import pyshark
import sys
import os
import numpy as np
import matplotlib.pyplot as plt 
from datetime import datetime


def processTimestamps(timestamps):
    # Convert timestamp is millis since first packet of the trace
    timestamps = np.array(timestamps) - timestamps[0]

    # to millis
    timestamps *= 100

    # substract previous times
    new_timestamps = []
    new_timestamps.append(timestamps[0])
    for i in range(1, len(timestamps)):
        new_timestamps.append(timestamps[i] - timestamps[i-1])

    print(timestamps[:10])
    print(new_timestamps[:10])
    return new_timestamps



def plot_IA(inFile):
    # read capture file
    capture = pyshark.FileCapture(inFile)
    
    # get timestamps and sizes
    timestamps = []
    for packet in capture:
        # if not ('OPENVPN' in packet):
        #     continue
        timestamps.append(float(packet.sniff_timestamp))
    
    # process timestamps
    timestamps = processTimestamps(timestamps)
    
    # create 2d hist and save
    plt.plot(timestamps)

    plt.xticks(range(len(timestamps))) # add loads of ticks
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*300+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])
    plt.ylim((0, 10))
    saveFile = f"{inFile.split('.')[0]}.png"
    plt.savefig(saveFile)
    plt.clf()

    capture.close()


ia_files_dir = os.path.join(os.getcwd(), "ia_traces")
print(ia_files_dir)
ia_files = os.listdir(ia_files_dir)
for f in ia_files:
    full_path = os.path.join(ia_files_dir, f)
    filepath = os.path.join(os.getcwd(), full_path)
    plot_IA(filepath)