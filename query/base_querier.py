import logging
from abc import ABC, abstractmethod
import requests
from typing import Dict, Any

class BaseQuerier(ABC):
    def __init__(self, url: str):
        self.url = url
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def get_transactions(self, start_timestamp: int, end_timestamp: int, skip: int = 0) -> Dict[str, Any]:
        """Abstract method to get transactions within a time period"""
        pass
    
    def _send_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Send GraphQL query and return response"""
        try:
            response = requests.post(
                self.url,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending GraphQL query: {str(e)}", exc_info=True)
            raise