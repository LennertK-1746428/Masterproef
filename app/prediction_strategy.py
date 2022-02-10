from urllib.request import parse_keqv_list
from config import *

def predict_strategy_1(packet_count, min_size, max_size, occ_size):
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


def predict_strategy_2(packet_count, min_size, max_size, occ_size):
    
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




def predict_traffic(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Traffic}
    top_2_set = set([occ_sizes[0][0], occ_sizes[1][0]])
    top_3_set = set([occ_sizes[0][0], occ_sizes[1][0], occ_sizes[2][0]])

    #######
    # TLS #
    #######

    # More than 0.5% TLS CLIENT HELLO 589 --> Browsing (Linux)
    if special_sizes[589][1] >= 0.5:
        scores[Traffic.BROWSING] += 1

    # More than 0.8% TLS CLIENT HELLO 577 --> Browsing (Windows)
    if special_sizes[577][1] >= 0.8:
        scores[Traffic.BROWSING] += 1

    #########################
    # Packet Size Frequency #
    #########################

    # Top 2 of 60,72 --> Browsing
    if set([60,72]) == top_2_set:
        scores[Traffic.BROWSING] += 1
    
    # 81 in top 3 --> streaming over QUIC
    if 81 in top_3_set:
        scores[Traffic.STREAMING_QUIC] += 1

    # a lot of ACKs (>= 80%) = streaming over HTTP
    return f"Traffic: {max(scores, key=scores.get).value}"


def predict_OS(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in OperatingSystem}
    
    #######
    # TLS #
    #######

    # More than 0.01% TLS CLIENT HELLO 589 --> Linux, else Windows
    if special_sizes[589][1] >= 0.01:
        scores[OperatingSystem.LINUX] += 1
    else:
        scores[OperatingSystem.WINDOWS] += 1
    
    # More than 0.8% TLS CLIENT HELLO 577 --> Windows (browsing)
    if special_sizes[577][1] >= 0.8:
        scores[OperatingSystem.WINDOWS] += 1

    #########################
    # Packet Size Frequency #
    #########################

    # Most occurring size of 72 --> Linux (streaming) 
    if occ_sizes[0][0] == 72:
        scores[OperatingSystem.LINUX] += 1

    return f"OS: {max(scores, key=scores.get).value}"


def predict_browser(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Browser}

    ##################
    # Traffic volume #
    ##################

    # Traffic amount < 2k/min --> Firefox (Streaming)
    if packets_per_min < 2000:
        scores[Browser.FIREFOX] += 1 

    # Traffic amount > 15k/min --> Firefox (Browsing)
    elif packets_per_min > 15000:
        scores[Browser.FIREFOX] += 1

    # Traffic amount > 2000 & < 15000 --> Chromium
    else:
        scores[Browser.EDGE] += 1
        scores[Browser.CHROME] += 1

    ###################
    # Max Packet Size #
    ###################

    # Only Firefox has max >= 1400 (1405) --> strong argument = +3
    if max_size >= 1400:
        scores[Browser.FIREFOX] += 3

    # Sometimes Edge has max <= 1321 (1298 or 1321)
    if max_size <= 1321:
        scores[Browser.EDGE] += 1

    #########################
    # Packet Size Frequency #
    #########################

    # Only Firefox seems to have most frequent size 81
    if occ_sizes[0][0] == 81:
        scores[Browser.FIREFOX] += 1

    return f"Browser: {max(scores, key=scores.get).value}"


def predict(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    
    traffic_prediction = "Traffic: "
    OS_prediction = "OS: "
    browser_prediction = "Browser: "

    top_3_set = set([occ_sizes[0][0], occ_sizes[1][0], occ_sizes[2][0]])
    top_2_set = set([occ_sizes[0][0], occ_sizes[1][0]])
    most_frequent_size = occ_sizes[0][0]

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

predict_traffic()