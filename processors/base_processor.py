from abc import ABC, abstractmethod
from typing import Dict, Any
from ..database.models import BaseTransaction

class BaseProcessor(ABC):
    def __init__(self, dex_id: str):
        self.dex_id = dex_id
    
    @abstractmethod
    def process_response(self, response_data: Dict[str, Any]) -> tuple[BaseTransaction, Dict[str, list]]:
        """Process the API response and return transaction and events"""
        pass