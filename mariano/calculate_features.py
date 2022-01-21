import os
from features_calculator import FeaturesCalculator

# file for writing output 
OUT_FILE = open("features_info.txt", "w")

# get all capture traces in this directory
files = os.listdir(os.getcwd())
files = [f for f in files if f.split('.')[-1] == "pcapng"]
files.sort()

# for every trace, calculate and output features
for f in files:
    OUT_FILE.write(f"{f.split('.')[0]}:\n")

    # get full filepath of the trace
    filePath = os.path.join(os.getcwd(), f)

    # calculate and output features
    calc = FeaturesCalculator(filePath, OUT_FILE)
    calc.calc_features()

# close output file
OUT_FILE.close()
    