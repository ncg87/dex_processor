import logging
from .queries import get_transactions_query
from .base_querier import BaseQuerier

class UniswapQuerier(BaseQuerier):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialized UniswapQuerier...")
    
    def get_transactions(self, start_timestamp, end_timestamp, skip):
        pass