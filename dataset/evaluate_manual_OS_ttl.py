import os 
from app.features_calculator import FeaturesCalculator
from app.prediction_strategy import predict 
import pyshark 

traces_dir = 'C:\\Users\\lenne\\Documents\\Masterproef_offline\\VPN_dataset_splitted' # ["webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming_quic", "webcrawlers/linux/traces/streaming_http", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming_quic", "webcrawlers/windows/traces/streaming_http"] 

# traces
traces = os.listdir(traces_dir)


# predict every trace
correct = 0
wrong = 0
current_trace = 0

for t in traces:
    current_trace += 1
    print(current_trace)

    # trace path
    in_path = os.path.join(traces_dir, t)

    # predict OS TTL
    capture = pyshark.FileCapture(in_path, display_filter="ip.src == 192.168.0.145")

    max_ttl = None
    for pkt in capture:
        max_ttl = int(pkt['IP'].ttl)
        break
    
    print(max_ttl)
    capture.close()

    # determine if assumption right or wrong 
    if max_ttl > 64:
        if "windows" in t:
            correct += 1
        else:
            wrong += 1
    else:
        if "windows" in t:
            wrong += 1
        else:
            correct += 1


print(f"Correct: {correct}")
print(f"Wrong: {wrong}")

"""
Correct: 1294
Wrong: 0
"""
