import logging
from typing import Dict
from .base_processor import BaseProcessor
from .uniswap_processor import UniswapV3Processor

logger = logging.getLogger(__name__)

class ProcessorFactory:
    _processors: Dict[str, type[BaseProcessor]] = {
        'uniswap_v3': UniswapV3Processor
    }
    
    @classmethod
    def get_processor(cls, dex_id: str) -> BaseProcessor:
        logger.debug(f"Attempting to get processor for DEX ID: {dex_id}")
        processor_class = cls._processors.get(dex_id)
        if not processor_class:
            logger.error(f"No processor found for DEX: {dex_id}")
            raise ValueError(f"No processor found for DEX: {dex_id}")
        logger.info(f"Created processor instance for DEX ID: {dex_id}")
        return processor_class()
    
    @classmethod
    def register_processor(cls, dex_id: str, processor_class: type[BaseProcessor]):
        logger.info(f"Registering new processor for DEX ID: {dex_id}")
        cls._processors[dex_id] = processor_class