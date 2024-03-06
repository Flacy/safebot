import logging
import sys

import loguru

from settings import config

LOG_LEVEL = logging.INFO if config.production else logging.DEBUG

logger = loguru.logger

# setup log level
logger.remove(0)
logger.add(sys.stderr, level=LOG_LEVEL)
