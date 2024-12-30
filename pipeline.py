"""pipeline.py"""
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from database import Database
from query import QuerierFactory
from processing import ProcessorFactory
from config.settings import Settings

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, dex_id: str = 'uniswap_v3'):
        """
        Initialize the data pipeline
        
        Args:
            dex_id: DEX identifier (default: 'uniswap_v3')
        """
        self.db = Database(Settings.POSTGRES_CONFIG)
        self.dex_id = dex_id
        self.querier = QuerierFactory.get_querier(dex_id)
        self.processor = ProcessorFactory.get_processor(dex_id)
        logger.info(f"Initialized DataPipeline for {dex_id}")
        
    def _process_batch(
        self,
        start_timestamp: int,
        end_timestamp: int,
        skip: int,
        batch_size: int,
        max_retries: int,
        retry_delay: int
    ) -> tuple[bool, int, int, int]:
        """
        Process a single batch of transactions
        
        Returns:
            tuple containing:
            - bool: Whether there are more transactions to process
            - int: Number of transactions processed in this batch
            - int: Number of events processed in this batch
            - int: Skip value for next batch
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Fetch data
                response = self.querier.get_transactions(
                    start_timestamp,
                    end_timestamp,
                    skip=skip
                )
                
                # Check if we have any transactions
                transactions = response.get('data', {}).get('transactions', [])
                if not transactions:
                    logger.info(f"No transactions found for skip={skip}")
                    return False, 0, 0, skip
                
                # Process transactions in bulk
                processed_events = self.processor.process_bulk_responses({
                    'data': {'transactions': transactions}
                })
                
                # Count total events
                total_events = sum(len(events) for events in processed_events)
                
                # Store data
                self.db.insert_transaction_batch(processed_events)
                
                # Determine if there are more transactions to process
                has_more = len(transactions) >= batch_size
                next_skip = skip + len(transactions)
                
                logger.debug(
                    f"Processed batch: {len(transactions)} transactions, "
                    f"{total_events} events, Skip: {skip}"
                )
                
                if skip % 10000 == 0:
                    logger.debug(
                    f"Processed batch: {len(transactions)} transactions, "
                    f"{total_events} events, Skip: {skip}"
                )
                # Return the results
                return has_more, len(transactions), total_events, next_skip
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(
                        f"Failed to process batch after {max_retries} attempts. "
                        f"Skip: {skip}, Error: {str(e)}"
                    )
                    raise
                logger.warning(
                    f"Retry {retry_count}/{max_retries} after error: {str(e)}. "
                    f"Waiting {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
        
        return False, 0, 0, skip

    def fetch_and_store_data(
        self, 
        start_timestamp: int,
        end_timestamp: int,
        batch_size: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> tuple[int, int]:
        """
        Fetch and store all data for a given time range with pagination
        
        Args:
            start_timestamp: Start timestamp (Unix)
            end_timestamp: End timestamp (Unix)
            batch_size: Optional override for Settings.BATCH_SIZE
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            tuple[int, int]: (Total transactions processed, Total events processed)
        """
        total_transactions = 0
        total_events = 0
        skip = 0
        batch_size = batch_size or Settings.BATCH_SIZE
        
        logger.info(
            f"Starting data collection from {datetime.fromtimestamp(start_timestamp)} "
            f"to {datetime.fromtimestamp(end_timestamp)}"
        )
        
        while True:
            has_more, batch_transactions, batch_events, next_skip = self._process_batch(
                start_timestamp,
                end_timestamp,
                skip,
                batch_size,
                max_retries,
                retry_delay
            )
            
            total_transactions += batch_transactions
            total_events += batch_events
            skip = next_skip
            
            if not has_more:
                break
            
            # Add a small delay between batches to avoid rate limiting
            time.sleep(0.5)
        
        logger.info(
            f"Completed data collection. Total transactions: {total_transactions}, "
            f"Total events: {total_events}"
        )
        
        return total_transactions, total_events

    def process_time_range(
        self,
        start_date: datetime,
        end_date: datetime,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> Dict[str, int]:
        """
        Process a date range
        
        Args:
            start_date: Start date
            end_date: End date
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dict[str, int]: Statistics about processed data
        """
        # Ensure partitions exist for the date range
        self.db.ensure_partitions(start_date, end_date)
        
        # Process data
        total_tx, total_events = self.fetch_and_store_data(
            int(start_date.timestamp()),
            int(end_date.timestamp()),
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        return {
            'transactions_processed': total_tx,
            'events_processed': total_events,
            'start_timestamp': int(start_date.timestamp()),
            'end_timestamp': int(end_date.timestamp())
        }

    def process_day(
        self,
        date: datetime,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> Dict[str, int]:
        """
        Process a full day of data
        
        Args:
            date: The date to process
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dict[str, int]: Statistics about processed data
        """
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        logger.info(f"Processing data for {date.date()}")
        
        return self.process_time_range(
            start_date,
            end_date,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize pipeline
        pipeline = DataPipeline()
        
        # Process yesterday's data
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        stats = pipeline.process_time_range(yesterday, now)
        
        logger.info(
            f"Successfully processed {yesterday.date()}: "
            f"Transactions: {stats['transactions_processed']}, "
            f"Events: {stats['events_processed']}"
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()