import logging
from typing import Dict, Optional
from database.database import Database

logger = logging.getLogger(__name__)

class VolumeTracker:
    def __init__(self, db: Database):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_volume_by_crypto(
        self, start_time: int, end_time: int, dex_id: str = None
    ) -> Dict[str, float]:
        """
        Calculate the total volume of each crypto using swaps, mints, and burns data.
        """
        
        self.logger.info(f"Calculating volume from {start_time} to {end_time} for DEX {dex_id or 'all DEXes'}")
        
        # Fetch events
        swaps = self.db.get_events_by_time("swaps", start_time, end_time, dex_id)
        mints = self.db.get_events_by_time("mints", start_time, end_time, dex_id)
        burns = self.db.get_events_by_time("burns", start_time, end_time, dex_id)

        crypto_volumes = {}
        logger.info(f"{len(swaps)} swaps, {len(mints)} mints, {len(burns)} burns queried...")
        # Process each event type
        for event in swaps:
            token0_id = event['token0_id']
            token1_id = event['token1_id']
            token0_symbol = event['token0_symbol']
            token1_symbol = event['token1_symbol']
            token0_name = event['token0_name']
            token1_name = event['token1_name']
            amount_usd = float(event['amount_usd'])
            
            # Aggregate volumes by token ID and symbol
            if token0_id not in crypto_volumes:
                crypto_volumes[token0_id] = {"id": token0_id, "symbol": token0_symbol, "name": token0_name, "volume": 0}
            if token1_id not in crypto_volumes:
                crypto_volumes[token1_id] = {"id": token1_id, "symbol": token1_symbol, "name": token1_name, "volume": 0}
            
            # Add to the total volume for each token
            crypto_volumes[token0_id]["volume"] += amount_usd
            crypto_volumes[token1_id]["volume"] += amount_usd

        # Convert volumes to a list for easy JSON serialization
        volume_list = list(crypto_volumes.values())
        
        # Sort the list by volume in descending order
        volume_list.sort(key=lambda x: x['volume'], reverse=True)
        
        self.logger.info(f"Volume calculation completed. Processed {len(swaps) + len(mints) + len(burns)} events.")
        return volume_list
    
    def get_volume_by_dex(self, start_time: int, end_time: int, crypto_id: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate the total volume of a specific crypto on each DEX.
        Args:
            crypto_id: The ID of the cryptocurrency to calculate volumes for.
            start_time: The start time as a UNIX timestamp.
            end_time: The end time as a UNIX timestamp.
        Returns:
            Dictionary with DEX IDs as keys and volumes as values.
        """
        dex_volumes = {}

        for event_type in ["swaps"]:
            events = self.db.get_crypto_events_by_time(event_type, start_time, end_time, crypto_id)
            for event in events:
                dex_id = event['dex_id']
                amount_usd = float(event['amount_usd'])
                
                if dex_id not in dex_volumes:
                    dex_volumes[dex_id] = 0.0
                dex_volumes[dex_id] += amount_usd

        return dex_volumes

