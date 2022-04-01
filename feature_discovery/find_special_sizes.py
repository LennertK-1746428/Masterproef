import os
from app.features_calculator import FeaturesCalculator

OUT_FILE = open("dataset_splitted__special_sizes_detection.txt", "w")
all_traces_dirs = ['C:\\Users\\lenne\\Documents\\VPN_dataset_splitted'] # ["webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming_quic", "webcrawlers/linux/traces/streaming_http", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming_quic", "webcrawlers/windows/traces/streaming_http"] 
sizes_dict = {}

for traces_dir in all_traces_dirs:

    # get all filenames in traces dir 
    files_dir = os.path.join(os.getcwd(), traces_dir)
    files = os.listdir(files_dir)
    files = [f for f in files if f.split('.')[-1] == "pcapng"]
    files.sort()
    print(files)

    # for every trace, calculate and output features
    i=0
    for f in files:
        i+=1
        print(i)

        filePath = os.path.join(files_dir, f)

        calc = FeaturesCalculator(trace=filePath)
        packet_count, min_size, max_size, occ_size, _ = calc.return_features()

        # single items
        for occ_tuple in occ_size:
            occ_item = occ_tuple[0]
            if occ_item not in sizes_dict:
                sizes_dict[occ_item] = []
            sizes_dict[occ_item].append(os.path.join(traces_dir, f))

        # two items
        for occ_tuple1 in occ_size:
            for occ_tuple2 in occ_size:
                if occ_tuple1[0] != occ_tuple2[0]:
                    occ_item = frozenset([occ_tuple1[0], occ_tuple2[0]])
                    if occ_item not in sizes_dict:
                        sizes_dict[occ_item] = []
                    sizes_dict[occ_item].append(os.path.join(traces_dir, f))

        # three items
        for occ_tuple1 in occ_size:
            for occ_tuple2 in occ_size:
                for occ_tuple3 in occ_size:
                    if len(set([occ_tuple1[0], occ_tuple2[0], occ_tuple3[0]])) == 3:
                        occ_item = frozenset([occ_tuple1[0], occ_tuple2[0], occ_tuple3[0]])
                        if occ_item not in sizes_dict:
                            sizes_dict[occ_item] = []
                        sizes_dict[occ_item].append(os.path.join(traces_dir, f))

# for key,val in sizes_dict.items():
#     OUT_FILE.write(f"{key} : {val}\n" )

def remove_dup(x):
  return list(dict.fromkeys(x))


def check_unique(key, vals, options):
    # get type of first element
    unique = True
    temp = ""
    for option in options:
        if option in vals[0]:
            temp = option  
            break

    # check if the type is the same for all elements
    for item in vals:
        if temp not in item:    # if another type in item --> type is not unique
            unique = False
            break
    
    if unique: # and len(vals) >= 3:
        OUT_FILE.write(f"{key} : {temp}, {len(vals)}x\n" )


for key,vals in sizes_dict.items():
    vals = remove_dup(vals)
    check_unique(key, vals, ["browsing", "streaming_twitch", "streaming_youtube"])      # traffic
    check_unique(key, vals, ["firefox", "edge", "chrome"])  # browser
    check_unique(key, vals, ["windows", "linux"])      # os

        
OUT_FILE.close()
    