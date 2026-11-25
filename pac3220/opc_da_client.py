"""OPC DA client used to write PAC3220 measurements into WinCC tags.

Runs on Windows only. WinCC Runtime must be active. Uses OpenOPC-DA
through the registered OPC DA Automation wrapper.
"""

import logging
import math
import platform
import time

from . import config

logger = logging.getLogger(__name__)


class WinCCOPCDAClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._last_connect_attempt = 0.0

    def connect(self, force=False):
        """Connect to the local WinCC OPC DA server."""
        if platform.system() != "Windows":
            raise RuntimeError("OPC DA is Windows COM/DCOM only.")

        if self.connected and self.client is not None:
            return True

        now = time.monotonic()
        if (not force and now - self._last_connect_attempt
                < config.OPC_DA_RECONNECT_SECONDS):
            return False
        self._last_connect_attempt = now

        try:
            import OpenOPC

            self.client = OpenOPC.client()
            result = self.client.connect(
                config.OPC_DA_SERVER, config.OPC_DA_HOST
            )
            if result is not True:
                raise ConnectionError(
                    f"OpenOPC could not connect to {config.OPC_DA_SERVER}"
                )

            self.connected = True
            logger.info(
                "Connected to WinCC OPC DA server %s on %s",
                config.OPC_DA_SERVER, config.OPC_DA_HOST
            )
            return True

        except Exception:
            self.connected = False
            if self.client is not None:
                try:
                    self.client.close()
                except Exception:
                    pass
            self.client = None
            logger.exception("WinCC OPC DA connection failed")
            return False

    def write_values(self, values, unverified_tags=None):
        """Batch-write {WinCC_ItemID: numeric_value}; return status map."""
        if not config.OPC_DA_ENABLED:
            return {}

        if not self.connected and not self.connect():
            return {name: "NOT_CONNECTED" for name in values}

        unverified_tags = unverified_tags or set()
        pairs = []
        skipped = {}

        for tag_name, value in values.items():
            if (config.OPC_DA_SKIP_UNVERIFIED_TAGS
                    and tag_name in unverified_tags):
                skipped[tag_name] = "SKIPPED_UNVERIFIED_REGISTER"
                continue
            if value is None:
                skipped[tag_name] = "SKIPPED_NONE"
                continue
            numeric_value = float(value)
            if not math.isfinite(numeric_value):
                skipped[tag_name] = "SKIPPED_NON_FINITE_VALUE"
                continue
            # For local WinCC project tags, ItemID is the tag name itself.
            pairs.append((tag_name, numeric_value))

        results = dict(skipped)
        if not pairs:
            return results

        try:
            # OpenOPC supports batch write and per-item status/error results.
            write_results = self.client.write(
                pairs, include_error=True
            )
            for item in write_results:
                tag_name = item[0]
                status = item[1]
                detail = item[2] if len(item) > 2 else ""
                results[tag_name] = status
                if str(status).lower() == "success":
                    logger.debug("OPC DA WRITE OK | %s", tag_name)
                else:
                    logger.error(
                        "OPC DA WRITE FAILED | %s | %s", tag_name, detail
                    )

            success_count = sum(
                1 for status in results.values()
                if str(status).lower() == "success"
            )
            failed_count = sum(
                1 for status in results.values()
                if status not in ("SKIPPED_UNVERIFIED_REGISTER",
                                  "SKIPPED_NONE",
                                  "SKIPPED_NON_FINITE_VALUE")
                and str(status).lower() != "success"
            )
            logger.info(
                "OPC DA WRITE CYCLE | Success=%d | Failed=%d | Skipped=%d",
                success_count, failed_count, len(skipped)
            )
            return results

        except Exception:
            logger.exception("OPC DA batch write failed; dropping connection")
            self.close()
            return {name: "WRITE_EXCEPTION" for name, _ in pairs} | results

    def read_tag(self, item_id):
        """Read one OPC item; returns OpenOPC (value, quality, timestamp)."""
        if not self.connected and not self.connect(force=True):
            raise ConnectionError("Not connected to WinCC OPC DA")
        return self.client.read(item_id)

    def close(self):
        if self.client is not None:
            try:
                self.client.close()
            except Exception:
                logger.exception("Error while closing OPC DA client")
        self.client = None
        self.connected = False
        logger.info("WinCC OPC DA connection closed")
