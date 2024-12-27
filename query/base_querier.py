import logging

logger = logging.getLogger(__name__)

class BaseQuerier:
    def __init__(self):
        self.logger.debug("Initialized BaseQuerier...")