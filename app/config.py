from enum import Enum

# the interval (in seconds) after which the packets will be analyzed to do predictions
CAPTURE_INTERVAL = 30


# Special sizes and their meaning 
class PacketTypes(Enum):
    TCP_ACK = "TCP ACK"
    TCP_ACK_OPTIONS = "TCP ACK WITH 12B OPTIONS"
    QUIC = "QUIC"
    TLS_KEY_EXCHANGE = "TLS KEY EXCHANGE"
    TLS_CLIENT_HELLO = "TLS CLIENT HELLO"
    TLS_CLIENT_HELLO_OPTIONS = "TLS CLIENT HELLO WITH 12B OPTIONS"


SPECIAL_SIZES = {
    60: PacketTypes.TCP_ACK,
    72: PacketTypes.TCP_ACK_OPTIONS,
    81: PacketTypes.QUIC,
    82: PacketTypes.QUIC,
    83: PacketTypes.QUIC,
    133: PacketTypes.TLS_KEY_EXCHANGE,
    145: PacketTypes.TLS_KEY_EXCHANGE,
    178: PacketTypes.TLS_KEY_EXCHANGE,
    199: PacketTypes.TLS_KEY_EXCHANGE,
    186: PacketTypes.TLS_KEY_EXCHANGE,
    218: PacketTypes.TLS_KEY_EXCHANGE,
    577: PacketTypes.TLS_CLIENT_HELLO,
    589: PacketTypes.TLS_CLIENT_HELLO_OPTIONS
}


def get_packet_type(size):
    """ Given the OpenVPN data size, return what kind of packet it is likely to be """

    if size in [60, 80]:           
        return PacketTypes.TCP_ACK
    if size in [72, 92]:
        return PacketTypes.TCP_ACK_OPTIONS
    if size in [81, 82, 83, 101, 102, 103]: # 3 IPv4, 3 IPv6
        return PacketTypes.QUIC
    if size in [577, 597]:
        return PacketTypes.TLS_CLIENT_HELLO
    if size in [589, 609]:
        return PacketTypes.TLS_CLIENT_HELLO_OPTIONS
    return None 


#############################
# Enums for classifications #
#############################

class Traffic(Enum):
    BROWSING = "Browsing"
    STREAMING_QUIC = "Streaming QUIC"
    STREAMING_HTTP = "Streaming HTTP"
    UPLOAD = "Uploading"

class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"

class Browser(Enum):
    FIREFOX = "Firefox"
    EDGE = "Edge"
    CHROME = "Chrome"