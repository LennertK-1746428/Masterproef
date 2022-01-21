import subprocess
import os

# specify interfaces
VPN_IFACE = "Local Area Connection"
REGULAR_IFACE = "WiFi"

# get IPs
VPN_IP = "172.27.234.4" 
REGULAR_IP = "192.168.0.145"

# determine filterS
vpn_filter = f"src host {REGULAR_IP} and udp port 1194"  
plain_filter = f"src host {VPN_IP}"

# determine output files
vpn_outfile = os.path.join(os.getcwd(), "traces/netflix", "windows_edge_vpn_1.pcapng")
plain_outfile = os.path.join(os.getcwd(), "traces/netflix", "windows_edge_plain_1.pcapng")

# keep capturing until a key is submitted
vpn_capture = subprocess.Popen(args=["tshark", "-i", REGULAR_IFACE, "-w", vpn_outfile, "-f", vpn_filter])
plain_capture = subprocess.Popen(args=["tshark", "-i", VPN_IFACE, "-w", plain_outfile, "-f", plain_filter])

input("Submit any key to terminate capturing..")

vpn_capture.terminate()
plain_capture.terminate()
