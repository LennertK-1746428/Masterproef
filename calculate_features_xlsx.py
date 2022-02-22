import os
import xlsxwriter
from app.features_calculator import FeaturesCalculator

# init Excel sheet
workbook = xlsxwriter.Workbook('features_webcrawlers.xlsx')
worksheet = workbook.add_worksheet("Features")
worksheet.write(0, 0, "Name")
worksheet.write(0, 2, "Packets/m")
worksheet.write(0, 3, "Min")
worksheet.write(0, 4, "Max")
worksheet.write(0, 6, "Top 3 occurrences: size - percentage")
worksheet.write(0, 13, "Special sizes: size - percentage - count")

all_traces_dirs = ["webcrawlers/linux/traces/browsing", "webcrawlers/linux/traces/streaming_quic", "webcrawlers/linux/traces/streaming_http", "webcrawlers/windows/traces/browsing", "webcrawlers/windows/traces/streaming_quic", "webcrawlers/windows/traces/streaming_http"] # ["android/traces", "linux/traces/browsing", "linux/traces/streaming", "windows/traces/browsing", "windows/traces/streaming"]
all_traces_dirs.sort()

row = 1
for traces_dir in all_traces_dirs:

    # get all filenames in traces dir 
    files_dir = os.path.join(os.getcwd(), traces_dir)
    files = os.listdir(files_dir)
    # files = [f for f in files if "vpn" in f and f.split('.')[-1] == "pcapng"]
    files = [f for f in files if "plain" not in f]
    files.sort()
    print(files)

    # notify which traces are being handled
    worksheet.write(row, 0, traces_dir)
    row += 1

    # for every trace, calculate and output features
    for f in files:
        worksheet.write(row, 0, f)

        filePath = os.path.join(files_dir, f)

        calc = FeaturesCalculator(trace=filePath)
        calc.write_features_xlsx(worksheet, row, 2)
        row += 1

workbook.close()
    