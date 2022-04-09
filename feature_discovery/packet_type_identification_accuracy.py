import os 
import pyshark

path = "G:\\My Drive\\Informatica\\Master\\Masterproef\\Code\\Repository\\random_traces\\traces\\IPv4_only\\vpn_plain"
files = os.listdir(path)
files = [f for f in files if "plain" in f]
tcp_ack_filter = "frame.len==54 or frame.len==74"
total_packets = 0
correct_packets = 0

print(files)

for f in files:
    print(f"Handling {f}")

    # init capture
    file_path = os.path.join(path, f)
    capture = pyshark.FileCapture(file_path, display_filter=tcp_ack_filter)

    # get length
    length = len([p for p in capture])
    total_packets += length

    # check which packets are correct (TCP ACK)
    for pkt in capture:
        if 'TCP' in pkt and int(pkt['TCP'].flags_ack) == 1:
            # print(dir(pkt['TCP']))
            # print(pkt['TCP'].flags)
            # print(pkt['TCP'].flags_ack)
            correct_packets += 1
             
    # close capture
    capture.close()
