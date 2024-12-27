from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class BaseTransaction:
    id: str             # Transaction ID
    dex_id: str         # DEX ID
    block_number: int   # Block number
    timestamp: int      # Timestamp
    gas_used: str       # Gas used
    gas_price: str      # Gas price
    
@dataclass
class SwapEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the swap
    id: str                             # Swap transaction ID   
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    amount0: str                        # Amount of token 0 in swap
    amount1: str                        # Amount of token 1 in swap
    amount_usd: str                     # Amount of USD of the swap (amount0 * token0_price or amount1 * token1_price)
    sender: str                         # Address of the sender
    recipient: str                      # Address of the recipient
    origin: str                         # Address of the origin
    fee_tier: int                       # Fee tier
    liquidity: str                      # Liquidity
    dex_id: str                         # DEX ID
    
@dataclass
class MintEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the mint
    id: str                             # Mint transaction ID
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    amount0: str                        # Amount of token 0 in mint
    amount1: str                        # Amount of token 1 in mint
    amount_usd: str                     # Amount of USD of the mint (amount0 * token0_price or amount1 * token1_price)
    sender: str                         # Address of the sender
    owner: str                          # Address of the owner
    origin: str                         # Address of the origin
    fee_tier: int                       # Fee tier
    liquidity: str                      # Liquidity
    dex_id: str                         # DEX ID

@dataclass
class BurnEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    
    timestamp: int                      # Timestamp of the burn
    id: str                             # Burn transaction ID
    token0_symbol: str                  # Token 0 symbol
    token1_symbol: str                  # Token 1 symbol
    amount0: str                        # Amount of token 0 in burn
    amount1: str                        # Amount of token 1 in burn
    amount_usd: str                     # Amount of USD of the burn (amount0 * token0_price or amount1 * token1_price)
    sender: str                         # Address of the sender
    owner: str                          # Address of the owner
    origin: str                         # Address of the origin
    fee_tier: int                       # Fee tier
    liquidity: str                      # Liquidity
    dex_id: str                         # DEX ID

# Worry about flash and collect events later, think I may need premium

@dataclass
class FlashEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    pass

@dataclass
class CollectEvent:
    parent_transaction: BaseTransaction # Info about the parent transaction
    pass