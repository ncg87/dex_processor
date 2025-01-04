from dataclasses import dataclass
from typing import Optional

# DEX Models #

@dataclass
class Token:
    id: str
    symbol: str
    name: str

@dataclass
class BaseTransaction:
    id: str                              # Transaction ID
    dex_id: str                          # DEX ID
    block_number: int                   # Block number
    timestamp: int                      # Timestamp
    gas_used: Optional[str] = None      # Gas used
    gas_price: Optional[str] = None     # Gas price
    
@dataclass
class SwapEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the swap
    id: str                             # Swap transaction ID   
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    token0_id: str                      # Token 0 ID
    token1_id: str                      # Token 1 ID
    token0_name: str                    # Token 0 name
    token1_name: str                    # Token 1 name
    amount0: str                        # Amount of token 0 in swap
    amount1: str                        # Amount of token 1 in swap
    amount_usd: str                     # Amount of USD of the swap (amount0 * token0_price or amount1 * token1_price)
    sender: str                         # Address of the sender
    recipient: str                      # Address of the recipient
    dex_id: str                         # DEX ID
    origin: Optional[str] = None        # Address of the origin
    fee_tier: Optional[int] = None      # Fee tier
    liquidity: Optional[str] = None     # Liquidity
    
@dataclass
class MintEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the mint
    id: str                             # Mint transaction ID
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    token0_id: str                      # Token 0 ID
    token1_id: str                      # Token 1 ID
    token0_name: str                    # Token 0 name
    token1_name: str                    # Token 1 name
    amount0: str                        # Amount of token 0 in mint
    amount1: str                        # Amount of token 1 in mint
    amount_usd: str                     # Amount of USD of the mint (amount0 * token0_price or amount1 * token1_price)
    owner: str                          # Address of the owner
    dex_id: str                         # DEX ID
    origin: Optional[str] = None        # Address of the origin
    fee_tier: Optional[int] = None      # Fee tier
    liquidity: Optional[str] = None     # Liquidity

@dataclass
class BurnEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the burn
    id: str                             # Burn transaction ID
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    token0_id: str                      # Token 0 ID
    token1_id: str                      # Token 1 ID
    token0_name: str                    # Token 0 name
    token1_name: str                    # Token 1 name
    amount0: str                        # Amount of token 0 in burn
    amount1: str                        # Amount of token 1 in burn
    amount_usd: str                     # Amount of USD of the burn (amount0 * token0_price or amount1 * token1_price)
    owner: str                          # Address of the owner
    dex_id: str                         # DEX ID
    origin: Optional[str] = None        # Address of the origin
    fee_tier: Optional[int] = None      # Fee tier
    liquidity: Optional[str] = None     # Liquidity

# Worry about flash and collect events later, think I may need premium

@dataclass
class FlashEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    pass

@dataclass
class CollectEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    pass
