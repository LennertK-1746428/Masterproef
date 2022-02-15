from enum import Enum

# the interval (in seconds) after which the packets will be analyzed to do predictions
CAPTURE_INTERVAL = 30

# Special sizes and their meaning 
SPECIAL_SIZES = {
    60: "TPC ACK",
    72: "TCP ACK",
    81: "QUIC",
    82: "QUIC",
    83: "QUIC",
    133: "TLS CLIENT KEY EXCHANGE",
    145: "TLS CLIENT KEY EXCHANGE",
    178: "TLS CLIENT KEY EXCHANGE",
    199: "TLS CLIENT KEY EXCHANGE",
    186: "TLS CLIENT KEY EXCHANGE",
    218: "TLS CLIENT KEY EXCHANGE",
    577: "TLS CLIENT HELLO",
    589: "TLS CLIENT HELLO"
}

# Enums for classifications 
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