"""
Scripts for parameterizing logging instance.
"""

import logging
from logging import (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)


def getLogger(name: str, logging_level: int = INFO):
    """
    Returns a logger object with timestamp
    information and terminal output
    """

    # sets logging output format
    logFormatter = logging.Formatter(
        "\n%(asctime)s [%(module)s] [%(funcName)s] [%(levelname)s] %(message)s")

    # sets StreamHandler object to output to terminal in formatted style
    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logFormatter)

    # sets logger object
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    if logger.hasHandlers():
        logger.handlers.clear()

    # bounds screen_handler to return logger
    logger.addHandler(screen_handler)

    return logger
