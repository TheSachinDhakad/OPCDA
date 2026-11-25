"""Modbus TCP connection and read-only register access."""

import logging

from pymodbus.client import ModbusTcpClient

from . import config


class PAC3220ModbusClient:
    def __init__(self):
        self.client = ModbusTcpClient(
            host=config.METER_IP,
            port=config.METER_PORT,
            timeout=config.CONNECT_TIMEOUT_SECONDS,
        )

    def connect(self):
        if self.client.connected:
            return True

        connected = self.client.connect()
        if connected:
            logging.info(
                "Connected to PAC3220 at %s:%s",
                config.METER_IP,
                config.METER_PORT,
            )
        else:
            logging.error(
                "Unable to connect to PAC3220 at %s:%s",
                config.METER_IP,
                config.METER_PORT,
            )
        return connected

    def read_registers(self, address, count):
        if not self.client.connected and not self.connect():
            raise ConnectionError("Modbus TCP connection is unavailable")

        if config.READ_FUNCTION == "input":
            response = self.client.read_input_registers(
                address=address,
                count=count,
                device_id=config.SLAVE_ID,
            )
        elif config.READ_FUNCTION == "holding":
            response = self.client.read_holding_registers(
                address=address,
                count=count,
                device_id=config.SLAVE_ID,
            )
        else:
            raise ValueError(
                "READ_FUNCTION must be either 'input' or 'holding'"
            )

        if response.isError():
            raise IOError(
                f"Modbus read error: address={address}, "
                f"count={count}, response={response}"
            )

        return response.registers

    def close(self):
        self.client.close()
        logging.info("Modbus connection closed")
