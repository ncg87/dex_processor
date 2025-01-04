from typing import Dict, Any, List, Tuple
from .base_processor import BaseProcessor
from database.models import BaseTransaction, SwapEvent, MintEvent, CollectEvent, BurnEvent, FlashEvent
import logging

logger = logging.getLogger(__name__)

class UniswapV2Processor(BaseProcessor):
    def __init__(self):
        super().__init__('uniswap_v2')
        self.logger.info("Initialized UniswapV2Processor...")

    def process_response(self, transaction_data: Dict[str, Any]) -> Dict:
        
        # Create base transaction
        transaction = BaseTransaction(
            id=transaction_data['id'],
            dex_id=self.dex_id,
            block_number=int(transaction_data['blockNumber']),
            timestamp=int(transaction_data['timestamp']),
        )
        
        #self.logger.debug(f"Processing transaction {transaction.id} from block {transaction.block_number}")
                
        # Process events
        events = {
            'swaps': self._process_swaps(transaction_data.get('swaps', []), transaction),
            'mints': self._process_mints(transaction_data.get('mints', []), transaction),
            'burns': self._process_burns(transaction_data.get('burns', []), transaction),
            'collects': self._process_collects(transaction_data.get('collects', []), transaction),
            'flashs': self._process_flashs(transaction_data.get('flashed', []), transaction),
        }
        #self.logger.debug(f"Processed events for transaction {transaction.id}: "
        #                    f"swaps={len(events['swaps'])}, mints={len(events['mints'])}, "
        #                    f"burns={len(events['burns'])}, collects={len(events['collects'])}, "
        #                    f"flashs={len(events['flashs'])}")
        
        return events
    
    def process_bulk_responses(self, bulk_response: Dict[str, Any]) -> List[Dict]:
        self.logger.debug(f"Processing bulk response on {self.dex_id} with {len(bulk_response.get('data', {}).get('transactions', []))} transactions")
        results = [[],[],[],[],[]]
        try:
            # Iterate through each transaction in response
            for transaction in bulk_response['data']['transactions']:
                events = self.process_response(transaction)
                
                # Append events to results
                results[0].extend(events['swaps'])
                results[1].extend(events['mints'])
                results[2].extend(events['burns'])
                results[3].extend(events['collects'])
                results[4].extend(events['flashs'])
            
            self.logger.debug(f"Processed {len(results[0])} swaps, {len(results[1])} mints, {len(results[2])} burns, {len(results[3])} collects, {len(results[4])} flashs for a total of {len(results[0]) + len(results[1]) + len(results[2]) + len(results[3]) + len(results[4])} events.")
        except Exception as e:
            self.logger.error(f"Error processing bulk response on {self.dex_id}: {e}", exc_info=True)
        return results
    
    def _process_swaps(self, swaps: List[Dict], transaction: BaseTransaction) -> List[SwapEvent]:
        try:
            swap_transactions = []
            for swap in swaps:
                swap_transaction = SwapEvent(
                    parent_transaction=transaction,
                    timestamp=int(swap['timestamp']),
                    id=swap['id'],
                    token0_symbol=swap['pair']['token0']['symbol'],
                    token1_symbol=swap['pair']['token1']['symbol'],
                    token0_id=swap['pair']['token0']['id'],
                    token1_id=swap['pair']['token1']['id'],
                    token0_name=swap['pair']['token0']['name'],
                    token1_name=swap['pair']['token1']['name'],
                    amount0=swap['amount0In'] if float(swap['amount0In']) > 0 else swap['amount0Out'],
                    amount1=swap['amount1In'] if float(swap['amount1In']) > 0 else swap['amount1Out'],
                    amount_usd=swap['amountUSD'],
                    sender=swap['sender'],
                    recipient=swap['to'],
                    dex_id=self.dex_id,
                )
                swap_transactions.append(swap_transaction)
                #self.logger.debug(f"Processed swap event {swap['id']} for transaction {transaction.id}")
            #self.logger.debug(f"Processed {len(swap_transactions)} swap events for transaction {transaction.id}")
        except Exception as e:
            self.logger.error(f"Error processing swaps on {self.dex_id}: {e}", exc_info=True)
            raise e
        
        return swap_transactions
    
    def _process_mints(self, mints: List[Dict], transaction: BaseTransaction) -> List[MintEvent]:
        try:
            mint_transactions = []
            for mint in mints:
                mint_transaction = MintEvent(
                    parent_transaction=transaction,
                    timestamp=int(mint['timestamp']),
                    id=mint['id'],
                    token0_symbol=mint['pair']['token0']['symbol'],
                    token1_symbol=mint['pair']['token1']['symbol'],
                    token0_id=mint['pair']['token0']['id'],
                    token1_id=mint['pair']['token1']['id'],
                    token0_name=mint['pair']['token0']['name'],
                    token1_name=mint['pair']['token1']['name'],
                    amount0=mint['amount0'],
                    amount1=mint['amount1'],
                    amount_usd=mint['amountUSD'],
                    owner=mint['to'],
                    dex_id=self.dex_id,
                    liquidity=mint['liquidity'],
                    origin=mint['sender'],
                )
                
                mint_transactions.append(mint_transaction)
                #self.logger.debug(f"Processed mint event {mint['id']} for transaction {transaction.id}")
            #self.logger.debug(f"Processed {len(mint_transactions)} mint events for transaction {transaction.id}")
        except Exception as e:
            self.logger.error(f"Error processing mints on {self.dex_id}: {e}", exc_info=True)
            raise e
        return mint_transactions
    
    def _process_burns(self, burns: List[Dict], transaction: BaseTransaction) -> List[BurnEvent]:
        try:
            burn_transactions = []
            for burn in burns:
                burn_transaction = BurnEvent(
                    parent_transaction=transaction,
                    timestamp=int(burn['timestamp']),
                    id=burn['id'],
                    token0_symbol=burn['pair']['token0']['symbol'],
                    token1_symbol=burn['pair']['token1']['symbol'],
                    token0_id=burn['pair']['token0']['id'],
                    token1_id=burn['pair']['token1']['id'],
                    token0_name=burn['pair']['token0']['name'],
                    token1_name=burn['pair']['token1']['name'],
                    amount0=burn['amount0'],
                    amount1=burn['amount1'],
                    amount_usd=burn['amountUSD'],
                    owner=burn['to'],
                    dex_id=self.dex_id,
                    liquidity=burn['liquidity'],
                    origin=burn['sender'],
                )
                burn_transactions.append(burn_transaction)
                #self.logger.debug(f"Processed burn event {burn['id']} for transaction {transaction.id}")
            #self.logger.debug(f"Processed {len(burn_transactions)} burn events for transaction {transaction.id}")
        except Exception as e:
            self.logger.error(f"Error processing burns on {self.dex_id}: {e}", exc_info=True)
            raise e
        return burn_transactions
    

    ## Don't exist in Uniswap V2 ##
    def _process_collects(self, collects: List[Dict], transaction: BaseTransaction) -> List[CollectEvent]:
        return []
    
    def _process_flashs(self, flashs: List[Dict], transaction: BaseTransaction) -> List[FlashEvent]:
        return []
    
    def _process_tokens(self, tokens_data: List[Dict]) -> List[Tuple]:
        try:
            tokens = [
                (
                    token['id'],
                    token['symbol'],
                    token['name']
                )
                for token in tokens_data.get("data", {}).get("tokens", [])
            ]  
            self.logger.debug(f"Processed {len(tokens)} tokens")
        except Exception as e:
            self.logger.error(f"Error processing tokens: {str(e)}", exc_info=True)
            raise e
        
        return tokens
