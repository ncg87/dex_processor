import logging
from typing import Dict
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
            token0 = event['token0_symbol']
            token1 = event['token1_symbol']
            amount_usd = float(event['amount_usd'])

            # Add to the total volume for each token
            crypto_volumes[token0] = crypto_volumes.get(token0, 0) + amount_usd
            crypto_volumes[token1] = crypto_volumes.get(token1, 0) + amount_usd

        self.logger.info(f"Volume calculation completed. Processed {len(swaps) + len(mints) + len(burns)} events.")
        return crypto_volumes
