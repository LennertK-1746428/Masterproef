from tokenize import Special
import pyshark
import numpy as np
from collections import Counter
from app.config import SPECIAL_SIZES


class FeaturesCalculator:

    def __init__(self, trace=None, capture=None):
        """ Constructor """
        self.trace = trace
        self.capture = capture
        self.packet_sizes = []
        self.ovpn_data_sizes = []
        self.timestamps = []
        self.ia_times = []
        self.duration_minutes = float(0)
    
    
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
    

    def __percentage(self, val, total):
        """ Calculate percentage """
        return round((float(val)/float(total))*100, 2)


    def __normalize_count(self, count):
        """ Normalized something that was counted by the time """
        return int(count/self.duration_minutes)


    def __calc_general_list_information(self, lst):
        """ Calculate min, max, mean, std, and most frequent occuring elems of list"""
        min_ = min(lst)
        max_ = max(lst)
        mean_ = np.mean(lst)
        std_ = np.std(lst)
        occurrence_counts = Counter(lst)
        most_frequent = occurrence_counts.most_common(3)
        most_frequent = [(key, self.__normalize_count(val), self.__percentage(val, len(lst))) for (key, val) in most_frequent]
        return min_, max_, mean_, std_, most_frequent
    

    def __calc_ovpn_special_sizes_information(self):
        """ Calculate special sizes counts and percentages for ovpn data sizes """
        
        occurrence_counts = Counter(self.ovpn_data_sizes)
        length = len(self.ovpn_data_sizes)
        stats = {}

        for size in SPECIAL_SIZES:
            occ = occurrence_counts[size]
            stats[size] = (self.__normalize_count(occ), self.__percentage(occ, length))
           
        return stats 


    def __collect_information(self):
        """ Collect necessary info to calculate features """

        # open capture if is None
        if self.capture is None:
            self.capture = pyshark.FileCapture(self.trace)
        
        # get sizes and timestamps 
        self.packet_sizes = []
        self.ovpn_data_sizes = []
        self.timestamps = []
        fails = 0
        for packet in self.capture: #._packets:
            if not ('OPENVPN' in packet):
                continue
            try:
                self.timestamps.append(float(packet.sniff_timestamp))
                self.ovpn_data_sizes.append(int(packet.openvpn.data.size))
                self.packet_sizes.append(int(packet.length))
            except Exception as e:
                fails += 1
        
        # Duration in minutes 
        norm_timestamps = np.array(self.timestamps) - self.timestamps[0]
        duration_seconds = float(norm_timestamps[-1])
        self.duration_minutes = duration_seconds / 60

        # close capture
        self.capture.close()


    def return_features(self):
        """ Collect information about the trace and calculate features based on this """
        
        self.__collect_information()
        
        # Packet count
        packets_per_min = self.__normalize_count(len(self.packet_sizes))

        # OpenVPN data sizes general
        min_size, max_size, mean_size, std_size, occ_sizes = self.__calc_general_list_information(self.ovpn_data_sizes)
        
        # OpenVPN data special sizes
        special_sizes = self.__calc_ovpn_special_sizes_information()

        return packets_per_min, min_size, max_size, occ_sizes, special_sizes

        
    def write_features_txt(self, outstream):
        """  Calculate and write features to TXT """

        self.__collect_information()

        # Packet count
        packets_per_min = self.__normalize_count(len(self.packet_sizes))
        outstream.write(f"Packets/m: {packets_per_min}\n")

        # OpenVPN data sizes
        min_size, max_size, mean_size, std_size, occ_sizes = self.__calc_general_list_information(self.ovpn_data_sizes)
        special_sizes = self.__calc_ovpn_special_sizes_information()

        outstream.write(f"Min ovpn data size: {min_size}\n")
        outstream.write(f"Max ovpn data size: {max_size}\n")
        # outstream.write(f"Mean ovpn data size: {round(mean_size, 2)}\n")
        # outstream.write(f"Std ovpn data size: {round(std_size, 2)}\n")
        outstream.write(f"Most frequent sizes: \n")
        for item in occ_sizes:
            outstream.write(f"\t{item[0]} - {item[2]}% - {item[1]}\n")
        outstream.write(f"Special sizes: \n")
        for (key, val) in special_sizes.items():
            outstream.write(f"\t{key} - {val[1]}% - {val[0]}\n")

        outstream.write('\n')

    
    def write_features_xlsx(self, worksheet, row, col):
        """ Calculate and write features to Excel """

        self.__collect_information()

        # Packet count
        packets_per_min = self.__normalize_count(len(self.packet_sizes))
        worksheet.write(row, col, packets_per_min)
        col += 1

        # OpenVPN data sizes
        min_size, max_size, mean_size, std_size, occ_sizes = self.__calc_general_list_information(self.ovpn_data_sizes)
        special_sizes = self.__calc_ovpn_special_sizes_information()
        
        worksheet.write(row, col, min_size); col += 1
        worksheet.write(row, col, max_size); col += 2
        
        for item in occ_sizes:
            worksheet.write(row, col, item[0]); col += 1
            worksheet.write(row, col, item[2]); col += 1
        for (key, val) in special_sizes.items():
            col += 1
            worksheet.write(row, col, key); col += 1
            worksheet.write(row, col, val[1]); col += 1
            worksheet.write(row, col, val[0]); col += 1
