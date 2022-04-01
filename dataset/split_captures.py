import subprocess
import os 

# Paths
input_path = 'C:\\Users\\lenne\\Documents\\Masterproef_offline\\VPN_dataset'
output_path = 'C:\\Users\\lenne\\Documents\\Masterproef_offline\\VPN_dataset_splitted'

# files
files = os.listdir(input_path)

for f in files:
    in_file_path = os.path.join(input_path, f)
    out_file_path = os.path.join(output_path, f)
    print(in_file_path)
    print(out_file_path)
    editcap_process = subprocess.Popen(args=["editcap", "-i", '60', in_file_path, out_file_path])

print("Done")