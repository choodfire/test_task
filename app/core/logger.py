import logging


def init_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(filename)s | %(message)s",
    )
