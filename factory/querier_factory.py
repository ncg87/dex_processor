import logging
from typing import Dict

from query import BaseQuerier, UniswapV3Querier, UniswapV2Querier, AerodromeQuerier, QuickswapV3Querier

from config.settings import Settings

logger = logging.getLogger(__name__)

class QuerierFactory:
    _queriers: Dict[str, tuple[type[BaseQuerier], str]] = {
        'uniswap_v3': (
            UniswapV3Querier,
            f"https://gateway.thegraph.com/api/{Settings.API_KEY}/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
        ),
        'uniswap_v2': (
            UniswapV2Querier,
            f"https://gateway.thegraph.com/api/{Settings.API_KEY}/subgraphs/id/A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"
        ),
        'aerodrome': (
            AerodromeQuerier,
            f"https://gateway.thegraph.com/api/{Settings.API_KEY}/subgraphs/id/GENunSHWLBXm59mBSgPzQ8metBEp9YDfdqwFr91Av1UM"
        ),
        'quickswap_v3': (
            QuickswapV3Querier,
            f"https://gateway.thegraph.com/api/{Settings.API_KEY}/subgraphs/id/FqsRcH1XqSjqVx9GRTvEJe959aCbKrcyGgDWBrUkG24g"
        ),
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