import subprocess
import os 

# all dirs with pcapng files that should be converted to pcap 
all_traces_dirs = ["webcrawlers/linux/traces/browsing"]#, "webcrawlers/linux/traces/streaming", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming"] # ["android/traces", "linux/traces/browsing", "linux/traces/streaming", "windows/traces/browsing", "windows/traces/streaming"]

for traces_dir in all_traces_dirs:

    # get all relevant in traces dir 
    files_dir = os.path.join(os.getcwd(), traces_dir)
    files = os.listdir(files_dir)
    files = [f for f in files if os.path.splitext(f)[1] == ".pcapng"]
    print(files)

    # convert all files to pcap
    for f in files:
        base_name = os.path.join(files_dir, os.path.splitext(f)[0])
        convert_process = subprocess.Popen(args=["tshark", "-F", "pcap", "-r", f"{base_name}.pcapng", "-w", f"{base_name}.pcap"])
