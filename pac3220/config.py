"""Configuration for the Siemens PAC3220 gateway."""

METER_IP = "10.0.11.51"
METER_PORT = 502
SLAVE_ID = 2

# Start a new polling cycle approximately every 1 second.
POLL_INTERVAL_SECONDS = 1.0

CONNECT_TIMEOUT_SECONDS = 3
RECONNECT_DELAY_SECONDS = 3

# "input" means Function Code 04. "holding" means Function Code 03.
READ_FUNCTION = "input"

# The current test used ABCD and returned plausible voltage/current/power values.
# Verify this against the official meter documentation and display.
FLOAT_WORD_ORDER = "ABCD"

# SCADA-style reference 400001 maps to protocol offset 1 in this project.
SCADA_REGISTER_BASE = 400000

LOG_LEVEL = "INFO"
LOG_FILE = "logs/gateway.log"


# WinCC OPC DA client configuration.
# WinCC Runtime must be active and the local WinCC OPC DA server registered.
OPC_DA_ENABLED = True
OPC_DA_SERVER = "OPCServer.WinCC"
OPC_DA_HOST = "localhost"
OPC_DA_RECONNECT_SECONDS = 5.0
OPC_DA_WRITE_TIMEOUT_SECONDS = 3.0

# The two tariff energy registers produced implausibly large values in the test log.
# Keep them out of WinCC until their register mapping and scaling are validated.
OPC_DA_SKIP_UNVERIFIED_TAGS = True
