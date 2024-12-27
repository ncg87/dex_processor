from typing import Dict
from .base_processor import BaseProcessor
from .uniswap_processor import UniswapProcessor

class ProcessorFactory:
    _processors: Dict[str, type[BaseProcessor]] = {
        'uniswap_v3': UniswapProcessor
    }
    
    @classmethod
    def get_processor(cls, dex_id: str) -> BaseProcessor:
        processor_class = cls._processors.get(dex_id)
        if not processor_class:
            raise ValueError(f"No processor found for DEX: {dex_id}")
        return processor_class()
    
    @classmethod
    def register_processor(cls, dex_id: str, processor_class: type[BaseProcessor]):
        cls._processors[dex_id] = processor_class