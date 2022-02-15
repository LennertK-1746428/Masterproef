import threading
import datetime
import pyshark
from config import *
from prediction_strategy import predict
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

        # if not enough traffic --> too idle to make predictions 
        if len_captured < 500:
            insert_label(f"{start_time} - {stop_time} || Too idle for predictions")
            continue

        # break if stop event set
        if threading.current_thread().stopped():
            break
        
        # get features
        features_calc = FeaturesCalculator(capture=capture)
        packets_per_min, min_size, max_size, occ_sizes, special_sizes = features_calc.return_features()
        # print(f"{packet_count} {min_size} {max_size} {occ_size}")
        
        # do predictions based on features
        prediction = predict(packets_per_min, min_size, max_size, occ_sizes, special_sizes)
        print(occ_sizes)
        
        # add prediction to GUI
        insert_label(f"{start_time} - {stop_time} || {prediction}")