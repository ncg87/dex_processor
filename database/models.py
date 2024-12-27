from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class BaseTransaction:
    id: str
    dex_id: str
    block_number: int
    timestamp: int
    gas_used: str
    gas_price: str
    
@dataclass
class SwapEvent(BaseTransaction):
    pool_id: str
    token0_symbol: str
    token1_symbol: str
    token0_decimals: int
    token1_decimals: int
    fee_tier: int
    liquidity: str
    sqrt_price: str
    token0_price: str
    token1_price: str
    sender: str
    recipient: str
    origin: str
    amount0: str
    amount1: str
    amount_usd: str
    sqrt_price_x96: str
    tick: int
    log_index: int
    
@dataclass
class MintEvent(BaseTransaction):
    pass

@dataclass
class BurnEvent(BaseTransaction):
    pass

@dataclass
class FlashEvent(BaseTransaction):
    pass

@dataclass
class CollectEvent(BaseTransaction):
    pass
