import logging
from pathlib import Path

from pac3220 import config
from pac3220.gateway import PAC3220Gateway


def setup_logging():
    log_path = Path(config.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )


if __name__ == "__main__":
    setup_logging()
    PAC3220Gateway().run_forever()
