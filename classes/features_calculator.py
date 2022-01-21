import pyshark
import numpy as np
from collections import Counter

class FeaturesCalculator:

    def __init__(self, trace=None, outstream=None, capture=None):
        """ Constructor """
        self.trace = trace
        self.outstream = outstream
        self.capture = capture
        self.packet_sizes = []
        self.ovpn_data_sizes = []
        self.timestamps = []
        self.ia_times = []
    
    
    def __calc_ia_times(self):
        """ Calculate interarrival times based on timestamps """
        # Convert timestamp is millis since first packet of the trace
        norm_timestamps = np.array(self.timestamps) - self.timestamps[0]

        # For every time, substract previous time
        self.ia_times = []
        for i in range(1, len(norm_timestamps)):
            self.ia_times.append(norm_timestamps[i] - norm_timestamps[i-1])

        # filter out ia times > 1 second, because these are probably just user idle signs
        self.ia_times = [i for i in self.ia_times if i < 1000]
    

    def __calc_list_information(self, lst):
        """ Calculate min, max, mean, std, and most frequent occuring elems of list"""
        min_ = min(lst)
        max_ = max(lst)
        mean_ = np.mean(lst)
        std_ = np.std(lst)
        occurence_count = Counter(lst)
        most_frequent = occurence_count.most_common(3)
        most_frequent = [(key, f"Count: {val} = {round((val/len(lst))*100, 2)}%") for (key, val) in most_frequent]
        return min_, max_, mean_, std_, most_frequent


    def __collect_information(self):
        """ Collect necessary info to calculate features """
        # open capture if is None
        if self.capture is None:
            self.capture = pyshark.FileCapture(self.trace)
            print("done")
            
        # get sizes and timestamps 
        self.packet_sizes = []
        self.ovpn_data_sizes = []
        self.timestamps = []
        fails = 0
        for packet in self.capture:
            if not ('OPENVPN' in packet):
                continue
            try:
                self.timestamps.append(float(packet.sniff_timestamp))
                self.ovpn_data_sizes.append(int(packet.openvpn.data.size))
                self.packet_sizes.append(int(packet.length))
            except Exception as e:
                fails += 1
        
        # info about failed packets if there are any
        # if fails > 0:
        #     self.outstream.write(f"Failed to process {fails} / {fails + len(self.packet_sizes)} packets")

        # close capture
        self.capture.close()


    def calc_and_return_features(self):
        """ Collect information about the trace and calculate features based on this """
        
        self.__collect_information()
        
        # Packet count
        packet_count = len(self.packet_sizes)
        
        # OpenVPN data sizes
        min_size, max_size, mean_size, std_size, occ_size = self.__calc_list_information(self.ovpn_data_sizes)
        
        return packet_count, min_size, max_size, occ_size

        
    def calc_and_write_features(self):
        """ Collect information about the trace and calculate features based on this """
        self.__collect_information()

        # Packet count
        self.outstream.write(f"Packet count: {len(self.packet_sizes)}\n")

        # OpenVPN data sizes
        min_size, max_size, mean_size, std_size, occ_size = self.__calc_list_information(self.ovpn_data_sizes)
        self.outstream.write(f"Min ovpn data size: {min_size}\n")
        self.outstream.write(f"Max ovpn data size: {max_size}\n")
        # self.outstream.write(f"Mean ovpn data size: {round(mean_size, 2)}\n")
        # self.outstream.write(f"Std ovpn data size: {round(std_size, 2)}\n")
        self.outstream.write(f"Most frequent items: {occ_size}\n")

        # Packet sizes
        # min_size, max_size, mean_size, std_size, occ_size = self.__calc_list_information(self.packet_sizes)
        # self.outstream.write(f"Min packet size: {min_size}\n")
        # self.outstream.write(f"Max packet size: {max_size}\n")
        # self.outstream.write(f"Mean packet size: {mean_size}\n")
        # self.outstream.write(f"Std packet size: {std_size}\n")
        # self.outstream.write(f"Most frequent items: {occ_size}\n")

        # interarrival times
        # self.__calc_ia_times()
        # min_ia, max_ia, mean_ia, std_ia = self.__calc_list_information(self.ia_times)
        # print(f"Min IA: {min_ia}")
        # print(f"Max IA: {max_ia}")
        # print(f"Mean IA: {mean_ia}")
        # print(f"Std IA: {std_ia}")

        self.outstream.write('\n')