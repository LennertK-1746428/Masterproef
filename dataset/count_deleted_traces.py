import os 
from app.features_calculator import FeaturesCalculator
from app.prediction_strategy import predict
import csv
import pyshark 

traces_dir = 'C:\\Users\\lenne\\Documents\\Masterproef_offline\\VPN_dataset_splitted' # ["webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming_quic", "webcrawlers/linux/traces/streaming_http", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming_quic", "webcrawlers/windows/traces/streaming_http"] 
traces = os.listdir(traces_dir)
total_dict = {}
deleted_dict = {}
remaining_dict = {}
count = 0

print(f"Total: {len(traces)}")

def add_to_dict(d, operating_system, browser, traffic):
    if operating_system not in d:
        d[operating_system] = 1
    else:
        d[operating_system] += 1
    if browser not in d:
        d[browser] = 1
    else:
        d[browser] += 1
    if traffic not in d:
        d[traffic] = 1
    else:
        d[traffic] += 1

# predict every trace
for t in traces:

    # keep track of where we are 
    count += 1
    if count % 10 == 0:
        print(f"{count} / {len(traces)}")

    # trace path
    in_path = os.path.join(traces_dir, t)

    # get classifications 
    splitted = t.split('-')
    operating_system = splitted[0]
    browser = splitted[1]
    traffic = splitted[2]

    add_to_dict(total_dict, operating_system, browser, traffic)

    try: 
        # get trace features
        capture = pyshark.FileCapture(in_path, display_filter="ip.src == 192.168.0.145")  # prediction only considers client --> server
        features_calc = FeaturesCalculator(capture=capture)
        packets_per_min, min_size, max_size, mean_size, std_size, unique_sizes, occ_sizes, special_sizes = features_calc.return_features()

        # skip if too few packets 
        if packets_per_min <= 50:
            add_to_dict(deleted_dict, operating_system, browser, traffic)
            print(f"Too few packets, skipping..")
            continue 
        
        add_to_dict(remaining_dict, operating_system, browser, traffic)

    except Exception as e:
        print(e)


print(f"Total: {total_dict}")
print(f"Deleted: {deleted_dict}")
print(f"Remaining: {remaining_dict}")

"""
Total: {'linux': 582, 'chrome': 398, 'browsing': 398, 'streaming_twitch': 349, 'streaming_youtube': 366, 'edge': 366, 'firefox': 349, 'windows': 531}
Deleted: {'linux': 84, 'chrome': 75, 'browsing': 98, 'streaming_twitch': 1, 'edge': 2, 'firefox': 23, 'streaming_youtube': 1, 'windows': 16}
Remaining: {'linux': 498, 'chrome': 323, 'browsing': 300, 'streaming_twitch': 348, 'streaming_youtube': 365, 'edge': 364, 'firefox': 326, 'windows': 515}
"""