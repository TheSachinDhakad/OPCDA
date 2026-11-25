"""PAC3220 Modbus TCP polling with WinCC OPC DA tag publishing."""

import logging
import time
from datetime import datetime

from . import config
from .decoder import decode_float32
from .modbus_client import PAC3220ModbusClient
from .opc_da_client import WinCCOPCDAClient
from .tags import TAGS, REGISTER_BLOCKS, UNVERIFIED_TAGS

logger = logging.getLogger(__name__)


class PAC3220Gateway:
    def __init__(self):
        
        self.modbus = PAC3220ModbusClient()
        self.opc_da = WinCCOPCDAClient() if config.OPC_DA_ENABLED else None
        self.tag_offsets = {
            name: scada_reference - config.SCADA_REGISTER_BASE
            for name, scada_reference, unit in TAGS
        }
        self.register_cache = {}

    def read_all_blocks(self):
        """Read configured Modbus blocks and cache registers by offset."""
        cache = {}
        for start_address, register_count in REGISTER_BLOCKS:
            registers = self.modbus.read_registers(
                address=start_address, count=register_count
            )
            for index, register_value in enumerate(registers):
                cache[start_address + index] = register_value
        self.register_cache = cache

    def decode_tag(self, tag_name):
        start_address = self.tag_offsets[tag_name]
        if start_address not in self.register_cache:
            raise KeyError(f"Missing register offset {start_address}")
        if start_address + 1 not in self.register_cache:
            raise KeyError(f"Missing register offset {start_address + 1}")
        raw_registers = [
            self.register_cache[start_address],
            self.register_cache[start_address + 1],
        ]
        return decode_float32(
            raw_registers, word_order=config.FLOAT_WORD_ORDER
        )

    def read_measurements(self):
        self.read_all_blocks()
        values, errors = {}, {}
        for tag_name, scada_reference, unit in TAGS:
            try:
                values[tag_name] = self.decode_tag(tag_name)
            except Exception as exc:
                errors[tag_name] = str(exc)
        return values, errors

    def publish_to_wincc(self, values):
        if self.opc_da is None:
            return {}
        return self.opc_da.write_values(
            values, unverified_tags=UNVERIFIED_TAGS
        )

    def display_measurements(self, timestamp, values, errors, opc_results=None):
        function_code = "04" if config.READ_FUNCTION == "input" else "03"
        print("\n" + "=" * 82)
        print("SIEMENS PAC3220 - MODBUS TCP + WINCC OPC DA GATEWAY")
        print("=" * 82)
        print(f"Timestamp: {timestamp}")
        print(f"Meter IP: {config.METER_IP}")
        print(f"Slave ID: {config.SLAVE_ID}")
        print(f"Function Code: {function_code}")
        print(f"OPC DA Server: {config.OPC_DA_SERVER if config.OPC_DA_ENABLED else 'Disabled'}")
        print("-" * 82)

        for tag_name, scada_reference, unit in TAGS:
            if tag_name in values:
                suffix = f" {unit}" if unit else ""
                verify_note = " [VERIFY]" if tag_name in UNVERIFIED_TAGS else ""
                opc_note = ""
                if opc_results is not None and tag_name in opc_results:
                    opc_note = f" | OPC DA: {opc_results[tag_name]}"
                print(
                    f"{tag_name:30}: {values[tag_name]:16.4f}"
                    f"{suffix}{verify_note}{opc_note}"
                )
            else:
                print(
                    f"{tag_name:30}: READ ERROR - "
                    f"{errors.get(tag_name, 'Unknown error')}"
                )

        print("-" * 82)
        print(f"Successful measurements: {len(values)}/{len(TAGS)}")
        if opc_results is not None:
            opc_success = sum(1 for v in opc_results.values()
                              if str(v).lower() == "success")
            print(f"Successful OPC DA writes: {opc_success}")
        print("=" * 82)

    def run_forever(self):
        logger.info("Starting PAC3220 Modbus + WinCC OPC DA Gateway")
        logger.info("Meter IP: %s", config.METER_IP)
        logger.info("Meter port: %s", config.METER_PORT)
        logger.info("Slave ID: %s", config.SLAVE_ID)
        logger.info("Read function: %s", config.READ_FUNCTION)
        logger.info("Word order: %s", config.FLOAT_WORD_ORDER)
        logger.info("Total configured tags: %s", len(TAGS))
        logger.info("WinCC OPC DA enabled: %s", config.OPC_DA_ENABLED)
        logger.info("WinCC OPC DA server: %s", config.OPC_DA_SERVER)

        if self.opc_da is not None and not self.opc_da.connect(force=True):
            logger.error(
                "Initial WinCC OPC DA connection failed. "
                "Modbus polling will continue and OPC DA will retry."
            )

        try:
            while True:
                cycle_started = time.monotonic()
                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]
                try:
                    values, errors = self.read_measurements()
                    opc_results = self.publish_to_wincc(values)
                    self.display_measurements(
                        timestamp, values, errors, opc_results
                    )
                    logger.info(
                        "READ CYCLE | Success=%d/%d | ReadErrors=%s",
                        len(values), len(TAGS), errors if errors else "None"
                    )
                except Exception:
                    logger.exception("Gateway read/publish cycle failed")
                    self.modbus.close()

                elapsed = time.monotonic() - cycle_started
                remaining = config.POLL_INTERVAL_SECONDS - elapsed
                if remaining > 0:
                    time.sleep(remaining)
                else:
                    logger.warning(
                        "Polling interval exceeded. Cycle duration: %.3fs",
                        elapsed
                    )

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            self.modbus.close()
            if self.opc_da is not None:
                self.opc_da.close()
            logger.info("PAC3220 Gateway stopped")
