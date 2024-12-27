from typing import Dict, Any, List
from .base_processor import BaseProcessor
from database.models import BaseTransaction, SwapEvent, MintEvent, CollectEvent, BurnEvent, FlashEvent
from dataclasses import asdict

class UniswapProcessor(BaseProcessor):
    def __init__(self):
        super().__init__('uniswap_v3')
    
    def process_response(self, response_data: Dict[str, Any]) -> tuple[BaseTransaction, Dict[str, list]]:
        transaction_data = response_data['data']['transactions'][0]
        
        # Create base transaction
        transaction = BaseTransaction(
            id=transaction_data['id'],
            dex_id=self.dex_id,
            block_number=int(transaction_data['blockNumber']),
            timestamp=int(transaction_data['timestamp']),
            gas_used=transaction_data['gasUsed'],
            gas_price=transaction_data['gasPrice']
        )
        # Process events
        events = {
            'swaps': self._process_swaps(transaction_data.get('swaps', []), transaction),
            'mints': self._process_mints(transaction_data.get('mints', []), transaction),
            'collects': self._process_collects(transaction_data.get('collects', []), transaction),
            'burns': self._process_burns(transaction_data.get('burns', []), transaction),
            'flashs': self._process_flashs(transaction_data.get('flashed', []), transaction)
        }
        
        return transaction, events
    
    def _process_swaps(self, swaps_data: List[Dict], transaction: BaseTransaction) -> List[SwapEvent]:
        
        # Check if there are any swap transactions, check for none
        if not len(swaps_data) > 0:
            return None
        
        # Get info from the swap transaction
        swap_transactions = []
        for swap in swaps_data:
            swap_transaction = SwapEvent(
                parent_transaction = transaction,
                timestamp = transaction.timestamp,
                id = swap['id'],
                token0_symbol = swap['pool']['token0']['symbol'],
                token1_symbol = swap['pool']['token1']['symbol'],
                amount0 = swap['amount0'],
                amount1 = swap['amount1'],
                amount_usd = swap['amountUSD'],
                sender = swap['sender'],
                recipient = swap['recipient'],
                origin = swap['origin'],
                fee_tier = swap['pool']['feeTier'],
                liquidity = swap['pool']['liquidity'],
                dex_id = self.dex_id
            )
            swap_transactions.append(swap_transaction)
            
        return swap_transactions
    
    def _process_mints(self, mints_data: List[Dict], transaction: BaseTransaction) -> List[MintEvent]:
        
        # Check if there are any mint transactions, check for none
        if not len(mints_data) > 0:
            return None
        
        mint_transactions = []
        for mint in mints_data:
            mint_transaction = MintEvent(
                parent_transaction = transaction,
                timestamp = transaction.timestamp,
                id = mint['id'],
                token0_symbol = mint['pool']['token0']['symbol'],
                token1_symbol = mint['pool']['token1']['symbol'],
                amount0 = mint['amount0'],
                amount1 = mint['amount1'],
                amount_usd = mint['amountUSD'],
                sender = mint['sender'],
                owner = mint['owner'],
                origin = mint['origin'],
                fee_tier = mint['pool']['feeTier'],
                liquidity = mint['pool']['liquidity'],
                dex_id = self.dex_id
            )
            mint_transactions.append(mint_transaction)
        return mint_transactions

    def _process_burns(self, burns_data: List[Dict], transaction: BaseTransaction) -> List[BurnEvent]:
        
        # Check if there are any burn transactions, check for none
        if not len(burns_data) > 0:
            return None
    
        burn_transactions = []
        for burn in burns_data:
            burn_transaction = BurnEvent(
                parent_transaction = transaction,
                timestamp = transaction.timestamp,
                id = burn['id'],
                token0_symbol = burn['pool']['token0']['symbol'],
                token1_symbol = burn['pool']['token1']['symbol'],
                amount0 = burn['amount0'],
                amount1 = burn['amount1'],
                amount_usd = burn['amountUSD'],
                sender = burn['sender'],
                owner = burn['owner'],
                origin = burn['origin'],
                fee_tier = burn['pool']['feeTier'],
                liquidity = burn['pool']['liquidity'],
                dex_id = self.dex_id
            )
            burn_transactions.append(burn_transaction)
        return burn_transactions
    
    def _process_collects(self, collects_data: List[Dict], transaction: BaseTransaction) -> List[CollectEvent]:
        
        # Check if there are any collect transactions, check for none
        if not len(collects_data) > 0:
            return None
        
        pass
    
        collect_transactions = []
        for collect in collects_data:
            collect_transaction = CollectEvent(
                parent_transaction = transaction,
                **collect
            )
            collect_transactions.append(collect_transaction)
        return collect_transactions
    
    
    def _process_flashs(self, flashs_data: List[Dict], transaction: BaseTransaction) -> List[FlashEvent]:
        
        # Check if there are any flash transactions, check for none
        if not len(flashs_data) > 0:
            return None
        
        pass
        
        flash_transactions = []
        for flash in flashs_data:
            flash_transaction = FlashEvent(
                parent_transaction = transaction,
                **flash
            )
            flash_transactions.append(flash_transaction)
            
        return flash_transactions

