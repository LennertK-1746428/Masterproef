import threading
import datetime
import pyshark
from config import *
from features_calculator import FeaturesCalculator


class StoppableThread(threading.Thread):
    """ Thread class with a stop() method to be used for the predictor. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def predict_strategy_initial(packet_count, min_size, max_size, occ_size):
    prediction = ""
    top_3_set = set([occ_size[0][0], occ_size[1][0], occ_size[2][0]])
    top_2_set = set([occ_size[0][0], occ_size[1][0]])
    most_frequent_size = occ_size[0][0]

    # Browser + traffic type 
    if max_size >= 1400:            # Only firefox has max size >= 1400
        prediction += "Firefox"
        if most_frequent_size == 81:    # If firefox has most frequent 81 --> streaming, else browsing
            prediction += " Streaming"
        else:
            prediction += " Browsing"
    else:
        prediction += "Chromium-based"
        if 60 in top_3_set and 72 in top_2_set:  # Browsing --> 60 72 always in top 2
            prediction += " Browsing"
        else:
            prediction += " Streaming"
    # OS
    if most_frequent_size == 72:    # most frequent 72 is unique for linux
        prediction += " Linux"
    if top_2_set == set([60, 81]):  # top 2 of 60 81 is unique for windows
        prediction += " Windows"


def predict_strategy(packet_count, min_size, max_size, occ_size):
    
    traffic_prediction = "Traffic: "
    OS_prediction = "OS: "
    browser_prediction = "Browser: "

    top_3_set = set([occ_size[0][0], occ_size[1][0], occ_size[2][0]])
    top_2_set = set([occ_size[0][0], occ_size[1][0]])
    most_frequent_size = occ_size[0][0]

    # Traffic type 
    if set([60,72]).issubset(top_3_set) or set([60,82]).issubset(top_3_set):
        traffic_prediction += "Browsing"
    elif 81 in top_3_set or 83 in top_3_set:
        traffic_prediction += "Streaming"
    else:
        traffic_prediction += "/"

    # Browser 
    if max_size >= 1400:     
        browser_prediction += "Firefox"
    else:
        browser_prediction += "Chromium-based"

    # OS
    if set([72, 84]).issubset(top_3_set):   
        OS_prediction += "Linux"
    elif top_2_set == set([60, 81]):  # top 2 of 60 81 is unique for windows
        OS_prediction += "Windows"
    else:
        OS_prediction += "/"
    
    return f"{OS_prediction} | {browser_prediction} | {traffic_prediction}"



def predict_traffic(insert_label, ip, iface, server_port, interval):
    """ Target function of predictor thread """

    print(f"Thread started: {ip} {iface} {server_port} {interval}")

    capture_filter = f"src host {ip} and udp port {server_port}"  

    while not threading.current_thread().stopped():
        
        # init live capture object
        capture = pyshark.LiveCapture(interface=iface, bpf_filter=capture_filter)

        # sniff packets for specified amount of seconds
        start_time = datetime.datetime.now().strftime("%H:%M:%S")
        capture.sniff(timeout=interval)
        stop_time = datetime.datetime.now().strftime("%H:%M:%S")
        len_captured = len([p for p in capture._packets])
        print(f"Finished sniffing.. {len_captured} packets captured")

        # if somehow no packets captured 
        if len_captured < 100:
            insert_label(f"{start_time} - {stop_time} : Not enough traffic")
            continue
        # break if stop event set
        if threading.current_thread().stopped():
            break
        
        # get features
        features_calc = FeaturesCalculator(capture=capture)
        packet_count, min_size, max_size, occ_size = features_calc.calc_and_return_features()
        print(f"{packet_count} {min_size} {max_size} {occ_size}")
        
        # do predictions based on features
        prediction = predict_strategy(packet_count, min_size, max_size, occ_size)

        # add prediction to GUI
        insert_label(f"{start_time} - {stop_time} | {prediction}")