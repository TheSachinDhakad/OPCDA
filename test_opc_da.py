"""Write/read-back test for one WinCC internal OPC DA tag."""

import logging
from pac3220 import config
from pac3220.opc_da_client import WinCCOPCDAClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

TEST_ITEM_ID = "PY_TEST"  # Create this as an internal Float tag in WinCC.
TEST_VALUE = 123.45

def main():
    client = WinCCOPCDAClient()
    try:
        if not client.connect(force=True):
            raise SystemExit(
                "Could not connect. Check active WinCC Runtime, OPC DA "
                "server registration, OPC Automation wrapper and bitness."
            )

        write_result = client.client.write(
            (TEST_ITEM_ID, TEST_VALUE), include_error=True
        )
        print("Write result:", write_result)

        read_result = client.read_tag(TEST_ITEM_ID)
        print("Read-back (value, quality, timestamp):", read_result)

        value, quality, timestamp = read_result
        if str(quality).lower() != "good":
            raise SystemExit(f"Bad OPC quality: {quality}")
        if value is None or abs(float(value) - TEST_VALUE) > 0.001:
            raise SystemExit(
                f"Read-back mismatch: expected {TEST_VALUE}, got {value}"
            )
        print("PASS: WinCC OPC DA write and read-back verified.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
