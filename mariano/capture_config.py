# Main interface = the interface on which encrypted VPN traffic (OpenVPN packets) will be sent to the VPN server
IFACE = "WiFi"

# The server port to which VPN traffic will be forwarded (required for capture filter). 1194 should be the default port
SERVER_PORT = 1194

# IP of the specified interface (required for capture filter)
IP = "192.168.0.145"

# The browser you will be using during the capture
BROWSER = "chrome"