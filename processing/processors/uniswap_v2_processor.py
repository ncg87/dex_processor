from typing import Dict, Any, List
from ..base_processor import BaseProcessor
from database.models import BaseTransaction, SwapEvent, MintEvent, CollectEvent, BurnEvent, FlashEvent
import logging

logger = logging.getLogger(__name__)

class UniswapV2Processor(BaseProcessor):
    def __init__(self):
        super().__init__('uniswap_v2')
        self.logger.info("Initialized UniswapV2Processor...")

    def process_response(self, transaction_data: Dict[str, Any]) -> Dict:
        pass
    
    def process_bulk_response(self, bulk_response: Dict[str, Any]) -> List[Dict]:
        pass
    
    def _process_swaps(self, swaps: List[Dict[str, Any]]) -> List[SwapEvent]:
        pass
    
    def _process_mints(self, mints: List[Dict[str, Any]]) -> List[MintEvent]:
        pass
    
    def _process_burns(self, burns: List[Dict[str, Any]]) -> List[BurnEvent]:
        pass
    
    
    ## Don't exist in Uniswap V2 ##
    def _process_collects(self, collects: List[Dict[str, Any]]) -> List[CollectEvent]:
        pass
    
    def _process_flashs(self, flashs: List[Dict[str, Any]]) -> List[FlashEvent]:
        pass
