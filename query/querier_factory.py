import logging
from typing import Dict
from .base_querier import BaseQuerier
from .uniswap_querier import UniswapV3Querier

logger = logging.getLogger(__name__)

class QuerierFactory:
    _queriers: Dict[str, tuple[type[BaseQuerier], str]] = {
        'uniswap_v3': (
            UniswapV3Querier,
            "https://gateway.thegraph.com/api/81099bb3190c1b75ed9d4fe9112c74ae/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
        )
    }
    
    @classmethod
    def get_querier(cls, dex_id: str) -> BaseQuerier:
        logger.debug(f"Attempting to get querier for DEX ID: {dex_id}")
        querier_info = cls._queriers.get(dex_id)
        
        if not querier_info:
            logger.error(f"No querier found for DEX: {dex_id}")
            raise ValueError(f"No querier found for DEX: {dex_id}")
            
        querier_class, url = querier_info
        logger.info(f"Created querier instance for DEX ID: {dex_id}")
        return querier_class(url)
    
        
    @classmethod
    def register_querier(cls, dex_id: str, querier_class: type[BaseQuerier], url: str):
        logger.info(f"Registering new querier for DEX ID: {dex_id}")
        cls._queriers[dex_id] = (querier_class, url)