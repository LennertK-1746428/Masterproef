from urllib.request import parse_keqv_list
from config import *

def predict_strategy_1_OUTDATED(packet_count, min_size, max_size, occ_size):
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


def predict_strategy_2_OUTDATED(packet_count, min_size, max_size, occ_size):
    
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


def process_scores(scores):

    # special case = all 0 --> unknown
    max_value = max(scores.values())
    if max_value == 0:
        return "Unknown"

    # Determine best key(s)
    best_value = -1
    key_string = ""
    for key, value in scores.items():
        if value > best_value:
            key_string = key.value 
            best_value = value 
        elif value == best_value:
            key_string += f" OR {key.value}"

    # Some special cases of results 
    if Browser.EDGE.value in key_string and Browser.CHROME.value in key_string:
        key_string = "Chromium based"
    if Traffic.STREAMING_HTTP.value in key_string and Traffic.STREAMING_QUIC.value in key_string:
        key_string = "Streaming"

    return key_string


def predict_traffic(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Traffic}
    top_2_set = set([occ_sizes[0][0], occ_sizes[1][0]])
    top_3_set = set([occ_sizes[0][0], occ_sizes[1][0], occ_sizes[2][0]])

    #######
    # TLS #
    #######

    # TLS CLIENT HELLO 589 or 577 --> Browsing, else Streaming
    if special_sizes[589][1] >= 0.5 or special_sizes[589][0] >= 40:
        print("589: occurs --> Browsing")
        scores[Traffic.BROWSING] += 1
    elif special_sizes[577][1] >= 0.5 or special_sizes[577][0] >= 40:
        print("577: occurs --> Browsing")
        scores[Traffic.BROWSING] += 1
    elif special_sizes[577][1] <= 0.2:
        print("Neither 577 nor 589 --> Streaming")
        scores[Traffic.STREAMING_QUIC] += 1
        scores[Traffic.STREAMING_HTTP] += 1

    # TLS KEY EXCHANGE --> Browsing (Windows)
    if special_sizes[186][1] >= 0.2:
        print("186: occurs --> Browsing")
        scores[Traffic.BROWSING] += 1

    #########################
    # Packet Size Frequency #
    #########################

    # Top 2 of 60,72 --> strong indication Browsing or Streaming over HTTP
    if set([60,72]) == top_2_set:
        scores[Traffic.BROWSING] += 1
        scores[Traffic.STREAMING_HTTP] += 1

        # Difference between HTTP streaming and browsing is hard to notice in the amount of ACKs, but streaming over HTTP 
        # should not produce as many TLS client hello's as browsing 
        if packets_per_min >= 20000:
            print("60, 72, packets>20k: Streaming HTTP")
            scores[Traffic.STREAMING_HTTP] += 1
        else:
            print("60, 72, packets<20k: Browsing")
            scores[Traffic.BROWSING] += 1

    # 81 or 83 in top 2 --> strong indication Streaming over QUIC
    if 81 in top_2_set or 83 in top_2_set: # or special_sizes[81][1] >= 6:
        print("81 or 83: in top 2 --> Streaming QUIC")
        scores[Traffic.STREAMING_QUIC] += 1

    # if result is Streaming, look for ACKs
    result = process_scores(scores)
    if result == "Streaming":
        # ACKs make up at least 80% --> HTTP, else QUIC
        if special_sizes[60][1] + special_sizes[72][1] >= 80:
            result = Traffic.STREAMING_HTTP.value
        else:
            result = Traffic.STREAMING_QUIC.value 

    return f"Traffic: {result}"


def predict_OS(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in OperatingSystem}
    
    #######
    # TLS #
    #######

    # More than 0.01% TLS CLIENT HELLO 589 --> Linux, else Windows
    if special_sizes[589][1] > 0.01 or special_sizes[589][0] >= 40:
        print("589: occurs --> Linux")
        scores[OperatingSystem.LINUX] += 1
    elif special_sizes[577][1] >= 0.5 or special_sizes[577][0] >= 40:
        print("589: does not occur but 577 does --> Windows")
        scores[OperatingSystem.WINDOWS] += 1
    
    # More than 0.8% TLS CLIENT HELLO 577 --> Windows (Browsing), if present but less --> Linux (Browsing)
    # if special_sizes[577][1] >= 0.8:
    #     print("577: occurs a lot --> Windows")
    #     scores[OperatingSystem.WINDOWS] += 1
    # elif special_sizes[577][1] >= 0.25:
    #     print("577: occurs a little bit --> Linux")
    #     scores[OperatingSystem.LINUX] += 1

    # TLS KEY EXCHANGE --> Windows (Browsing)
    if special_sizes[186][1] >= 0.2:
        print("186: occurs a lot --> Windows")
        scores[OperatingSystem.WINDOWS] += 1

    #########################
    # Packet Size Frequency #
    #########################

    # Linux likes to send a lot of ACKs with 12B options 
    if occ_sizes[0][0] == 72 or special_sizes[72][1] >= 40:
        print("72: occurs a lot --> Linux")
        scores[OperatingSystem.LINUX] += 1

    return f"OS: {process_scores(scores)}"


def predict_browser(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Browser}

    ##################
    # Traffic volume #
    ##################

    # # Traffic amount < 2k/min --> Firefox (Streaming)
    # if packets_per_min < 2000:
    #     scores[Browser.FIREFOX] += 1 

    # # Traffic amount > 15k/min --> Firefox (Browsing)
    # elif packets_per_min > 15000:
    #     scores[Browser.FIREFOX] += 1

    # # Traffic amount > 2000 & < 15000 --> Chromium
    # else:
    #     scores[Browser.EDGE] += 1
    #     scores[Browser.CHROME] += 1

    ###################
    # Max Packet Size #
    ###################

    print(f"Max size: {max_size}")

    # Only Firefox has max >= 1400 (1405) --> strong argument = +3
    if max_size >= 1400:
        scores[Browser.FIREFOX] += 3
    else:
        scores[Browser.CHROME] += 3
        scores[Browser.EDGE] += 3

    # Sometimes Edge has max <= 1300 (1298)
    if max_size <= 1300:
        scores[Browser.EDGE] += 1

    return f"Browser: {process_scores(scores)}"


def predict(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    
    traffic = predict_traffic(packets_per_min, min_size, max_size, occ_sizes, special_sizes)
    OS = predict_OS(packets_per_min, min_size, max_size, occ_sizes, special_sizes)
    browser = predict_browser(packets_per_min, min_size, max_size, occ_sizes, special_sizes)

    return f"{OS} | {browser} | {traffic}"
