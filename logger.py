import logging

logging.CHAR_LEVELS = {
    "DEBUG": "*",
    "INFO": "+",
    "WARNING": "!",
    "ERROR": "X",
    "CRITICAL": "X!",
}


class CharFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in logging.CHAR_LEVELS:
            record.levelname = logging.CHAR_LEVELS[levelname]
        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = CharFormatter("[%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
