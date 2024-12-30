from .base_pipeline import BasePipeline
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class UniswapV3Pipeline(BasePipeline):
    def __init__(self, db, querier, processor):
        super().__init__(db, querier, processor)
        logger.info(f"Initialized UniswapV3Pipeline")
        
    def fetch_data(self, start_timestamp, end_timestamp, skip : int) -> List[Dict[str, Any]]:
        """Fetch data from Uniswap."""
        
        # Convert datetime to UNIX timestamps if needed
        if isinstance(start_timestamp, datetime):
            start_timestamp = int(start_timestamp.timestamp())
        if isinstance(end_timestamp, datetime):
            end_timestamp = int(end_timestamp.timestamp())
            
        logger.debug(f"Fetching Uniswap data: {start_timestamp} to {end_timestamp}, skip={skip}")
        return self.querier.get_transactions(start_timestamp, end_timestamp, skip=skip)
