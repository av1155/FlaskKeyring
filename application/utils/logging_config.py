import logging
import sys


def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.info("Logging setup complete")
