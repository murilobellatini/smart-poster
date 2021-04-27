"""
Scripts for parameterizing logging instance.
"""

import logging
from src.paths import LOCAL_GLOBAL_DATA
from logging import (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)


def getLogger(name: str, logging_level: int = DEBUG):
    """
    Returns a logger object with timestamp
    information and terminal output
    """

    # sets logging output format
    logFormatter = logging.Formatter(
        "%(asctime)s [%(module)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s")

    # sets StreamHandler object to output to terminal in formatted style
    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(logFormatter)

    file_handler = logging.FileHandler(
        LOCAL_GLOBAL_DATA / 'application.log')
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logFormatter)

    # sets logger object
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    if logger.hasHandlers():
        logger.handlers.clear()

    # bounds screen_handler to return logger
    logger.addHandler(screen_handler)
    logger.addHandler(file_handler)

    return logger
