import sys
import logging
from colorlog import ColoredFormatter

LOG_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
}

LOGFORMAT = (
    "  %(log_color)s %(levelname)-8s%(reset)s"
    + " %(log_color)s{%(filename)s:%(lineno)s} : %(message)s%(reset)s"
)

file_handler = logging.FileHandler(filename="lynx.log")
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(formatter)
stream.setLevel(logging.DEBUG)

handlers = [file_handler, stream]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d}"
    + " %(levelname)s - %(message)s",
    handlers=handlers,
)

log = logging.getLogger("pythonConfig")


def dbg(level):
    global logger

    log.setLevel(LOG_LEVELS[level])

    switcher = {
        "CRITICAL": log.critical,
        "WARNING": log.warning,
        "ERROR": log.error,
        "DEBUG": log.debug,
        "INFO": log.info,
    }

    return switcher[level]
