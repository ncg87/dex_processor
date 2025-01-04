import logging
from typing import Dict, Any
from .base_querier import BaseQuerier
from .queries import get_uniswap_v2_query, get_uniswap_v2_tokens_query

class UniswapV2Querier(BaseQuerier):
    def __init__(self, url: str):
        super().__init__(url)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialized UniswapV2Querier...")

    def get_transactions(self, start_timestamp: int, end_timestamp: int, skip: int = 0) -> Dict[str, Any]:
        variables = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "skip": skip
        }
        variables = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "skip": skip
        }
        try:
            response = self._send_query(get_uniswap_v2_query(), variables)
            self.logger.debug(
                f"Retrieved {len(response.get('data', {}).get('transactions', []))} "
                f"transactions between {start_timestamp} and {end_timestamp}"
            )
            return response
        except Exception as e:
            self.logger.error(f"Error getting transactions: {str(e)}", exc_info=True)
            raise
    
    def get_tokens(self, skip: int = 0) -> Dict[str, Any]:
        """
        Get tokens from the specified DEX subgraph
        """
        variables = {
            "first": 1000,
            "skip": skip
        }
        try:
            response = self._send_query(get_uniswap_v2_tokens_query(), variables)
            self.logger.debug(f"Retrieved {len(response.get('data', {}).get('tokens', []))} tokens")
            return response
        except Exception as e:
            self.logger.error(f"Error getting tokens: {str(e)}", exc_info=True)
            raise
