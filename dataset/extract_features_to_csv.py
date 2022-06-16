import os 
from app.features_calculator import FeaturesCalculator
from app.prediction_strategy import predict
import csv
import pyshark 

traces_dir = 'C:\\Users\\lenne\\Documents\\Masterproef_offline\\VPN_dataset_splitted' # ["webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming_quic", "webcrawlers/linux/traces/streaming_http", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming_quic", "webcrawlers/windows/traces/streaming_http"] 
traces = os.listdir(traces_dir)
features = []
predictions = []
count = 0
skip_prediction = 0

print(f"Total: {len(traces)}")

# classification matching
os_classify = {
    "windows": 0,
    "linux": 1,
    "unknown": 2
}
browser_classify = {
    "chrome": 0,
    "edge": 1,
    "chromium": 2,
    "firefox": 3,
    "unknown": 4
}
traffic_classify = {
    "browsing": 0,
    "streaming_youtube": 1,
    "streaming_twitch": 2,
    "unknown": 3
}
def get_classifications(s):
    """ return classification integers for os, browser, traffic """
    s = s.upper()
    Os = 0;  browser = 0; traffic = 0

    if "WINDOWS" in s: Os = os_classify["windows"]
    elif "LINUX" in s: Os = os_classify["linux"]
    else: Os = os_classify["unknown"]

    if "CHROMIUM" in s: browser = browser_classify["chromium"]
    elif "CHROME" in s: browser = browser_classify["chrome"]
    elif "EDGE" in s: browser = browser_classify["edge"]
    elif "FIREFOX" in s: browser = browser_classify["firefox"]
    else: browser = browser_classify["unknown"]

    if "TWITCH" in s: traffic = traffic_classify["streaming_twitch"]
    elif "YOUTUBE" in s: traffic = traffic_classify["streaming_youtube"]
    elif "BROWSING" in s: traffic = traffic_classify["browsing"]
    else: traffic = traffic_classify["unknown"]

    return Os, browser, traffic 


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

    try: 
        # get trace features
        capture = pyshark.FileCapture(in_path, display_filter="ip.src == 192.168.0.145")  # prediction only considers client --> server
        features_calc = FeaturesCalculator(capture=capture)
        packets_per_min, min_size, max_size, mean_size, std_size, unique_sizes, occ_sizes, special_sizes = features_calc.return_features()
        max_ttl = features_calc.return_max_ttl()

        # skip if too few packets 
        if packets_per_min <= 50:
            skip_prediction += 1
            print(f"Too few packets, skipping.. {skip_prediction} skipped")
            continue 

        # create features entry for csv
        features_item = [operating_system, browser, traffic, packets_per_min, min_size, max_size, mean_size, std_size, unique_sizes, max_ttl]
        for i in occ_sizes:
            features_item.append(i[0])
            features_item.append(i[1])
        for i in special_sizes.values():
            features_item.append(i[0])
            features_item.append(i[1])
        features.append(features_item)

        # predict and create prediction entry for csv
        prediction = predict(packets_per_min, min_size, max_size, None, occ_sizes, special_sizes)
        OS_predict, browser_predict, traffic_predict = get_classifications(prediction)
        predictions_item = [os_classify[operating_system], OS_predict, '', browser_classify[browser], browser_predict, '', traffic_classify[traffic], traffic_predict]
        predictions.append(predictions_item)

        print(f"{t} | {prediction} | {packets_per_min}")
        
    except Exception as e:
        print(e)

with open("dataset_splitted_features_sender_only.csv", "w", newline="") as f1:
    writer = csv.writer(f1)
    writer.writerows(features)

with open("dataset_splitted_predictions_manual_new_pred_strategy.csv", "w", newline="") as f2:
    writer = csv.writer(f2)
    writer.writerows(predictions)


print(f"Skipped {skip_prediction} traces, {len(traces)} - {skip_prediction} = {len(traces) - skip_prediction} used")


"""
Predictions: Skipped 100 traces, leaving 1113 - 100 = 1013 included
"""