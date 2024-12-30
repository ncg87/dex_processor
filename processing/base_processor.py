import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from database.models import BaseTransaction

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    def __init__(self, dex_id: str):
        self.dex_id = dex_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized {self.__class__.__name__} for {dex_id}")
    
    @abstractmethod
    def process_response(self, response_data: Dict[str, Any]) -> tuple[BaseTransaction, Dict[str, list]]:
        """Process the API response and return transaction and events"""
        pass