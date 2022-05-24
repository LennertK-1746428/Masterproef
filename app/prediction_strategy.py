from app.config import *


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
    if OperatingSystem.WINDOWS.value in key_string and OperatingSystem.LINUX.value in key_string:
        key_string = "Unknown"
    if Browser.EDGE.value in key_string and Browser.CHROME.value in key_string:
        key_string = "Chromium based"
    if Traffic.STREAMING_HTTP.value in key_string and Traffic.STREAMING_QUIC.value in key_string:
        key_string = "Streaming"

    return key_string


def predict_traffic(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Traffic}
    top_2_set = set([occ_sizes[0][0], occ_sizes[1][0]])
    top_3_set = set([occ_sizes[0][0], occ_sizes[1][0], occ_sizes[2][0]])

    ####################
    # TLS Client Hello #
    ####################

    # TLS CLIENT HELLO frequent --> Browsing
    if (special_sizes[PacketTypes.TLS_CLIENT_HELLO_OPTIONS][0] + special_sizes[PacketTypes.TLS_CLIENT_HELLO][0]) >= 15:
        if __debug__: print("TLS Client Hello occurs frequently --> Browsing")
        scores[Traffic.BROWSING] += 1
    else:
        # TCP ACKs >= 50% --> Twitch
        if (special_sizes[PacketTypes.TCP_ACK][1] + special_sizes[PacketTypes.TCP_ACK_OPTIONS][1]) >= 50:
            if __debug__: print("High number of TCP ACKs --> Twitch")
            scores[Traffic.STREAMING_HTTP] += 1
        # QUIC ACKs >= 30% --> YouTube
        if special_sizes[PacketTypes.QUIC][1] >= 30:
            if __debug__: print("High number of QUIC ACKs --> YouTube")
            scores[Traffic.STREAMING_QUIC] += 1
        # No YouTube nor Twitch indication --> Browsing
        if ((special_sizes[PacketTypes.TCP_ACK][1] + special_sizes[PacketTypes.TCP_ACK_OPTIONS][1]) < 50) and (special_sizes[PacketTypes.QUIC][1] < 30):
            if __debug__: print("Low number of TCP ACKs and low number of QUIC ACKs --> Browsing")
            scores[Traffic.BROWSING] += 1

    result = process_scores(scores)

    # if result is Streaming (same score for YouTube and Twitch), look at traffic volume 
    if result == "Streaming":
        if packets_per_min > 6000:
            if __debug__: print("High packet rate --> Twitch")
            result = Traffic.STREAMING_HTTP.value
        else:
            if __debug__: print("Low packet rate --> YouTube")
            result = Traffic.STREAMING_QUIC.value 

    return f"Traffic: {result}"


def predict_OS_max_ttl(max_ttl):
    if max_ttl > 64:
        return "OS: Windows"
    else:
        return "OS: Linux"


def predict_OS(packets_per_min, min_size, max_size, max_ttl, occ_sizes, special_sizes):

    #######
    # TTL #
    #######

    if max_ttl is not None:
        return predict_OS_max_ttl(max_ttl)

    scores = {key: 0 for key in OperatingSystem}
    
    ###################
    # TCP ACK Options #
    ###################

    # at least 15% TCP ACK with options --> Linux
    if special_sizes[PacketTypes.TCP_ACK_OPTIONS][1] >= 15:
        scores[OperatingSystem.LINUX] += 1
    # at least 70% TCP ACK without options --> Linux
    if special_sizes[PacketTypes.TCP_ACK][1] >= 70:
        scores[OperatingSystem.WINDOWS] += 1

    #######
    # TLS #
    #######

    # At least 5 TLS CLIENT HELLO WITH OPTIONS --> Linux
    if special_sizes[PacketTypes.TLS_CLIENT_HELLO_OPTIONS][0] >= 5:
        if __debug__: print("High number of TLS Client Hello with option --> Linux")
        scores[OperatingSystem.LINUX] += 1
    # At least 20 TLS CLIENT HELLO WITH OPTIONS --> Windows
    if special_sizes[PacketTypes.TLS_CLIENT_HELLO][0] >= 20:
        if __debug__: print("High number of TLS Client Hello without option--> Windows")
        scores[OperatingSystem.WINDOWS] += 1


    return f"OS: {process_scores(scores)}"


def predict_browser(packets_per_min, min_size, max_size, occ_sizes, special_sizes):
    scores = {key: 0 for key in Browser}

    ###################
    # Max Packet Size #
    ###################

    # Only Firefox has max >= 1400 (1405) 
    if max_size >= 1400:
        if __debug__: print("Max packet size >= 1400 --> Firefox")
        scores[Browser.FIREFOX] += 1
    else:
        if __debug__: print("Max packet size < 1400 --> Chromium")
        scores[Browser.CHROME] += 1
        scores[Browser.EDGE] += 1

    return f"Browser: {process_scores(scores)}"


def predict(packets_per_min, min_size, max_size, max_ttl, occ_sizes, special_sizes):
    
    traffic = predict_traffic(packets_per_min, min_size, max_size, occ_sizes, special_sizes)
    OS = predict_OS(packets_per_min, min_size, max_size, max_ttl, occ_sizes, special_sizes)
    browser = predict_browser(packets_per_min, min_size, max_size, occ_sizes, special_sizes)

    classification =  f"{OS} | {browser} | {traffic}"
    if __debug__: print(f"Classification: {classification}\n==============================")

    return classification
