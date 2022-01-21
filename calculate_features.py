import os
from classes.features_calculator import FeaturesCalculator

OUT_FILE = open("netflix_info.txt", "w")
all_traces_dirs = ["random_traces/traces/netflix"] #"webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming"] # ["android/traces", "linux/traces/browsing", "linux/traces/streaming", "windows/traces/browsing", "windows/traces/streaming"]

for traces_dir in all_traces_dirs:

    # get all filenames in traces dir 
    files_dir = os.path.join(os.getcwd(), traces_dir)
    files = os.listdir(files_dir)
    files = [f for f in files if "vpn" in f and f.split('.')[-1] == "pcapng"]
    files.sort()
    print(files)

    # notify which traces are being handled
    OUT_FILE.write('-----\n')
    OUT_FILE.write(f"{traces_dir}\n")
    OUT_FILE.write('-----\n')

    # for every trace, calculate and output features
    for f in files:
        OUT_FILE.write(f"{f}:\n")

        filePath = os.path.join(files_dir, f)

        calc = FeaturesCalculator(trace=filePath, outstream=OUT_FILE)
        calc.calc_and_write_features()

OUT_FILE.close()
    