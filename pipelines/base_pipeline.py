from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
from factory.querier_factory import QuerierFactory
from factory.processor_factory import ProcessorFactory
from database.database import Database
import time

logger = logging.getLogger(__name__)

class BasePipeline(ABC):
    def __init__(self, db, querier, processor, batch_size=1000):
        """
        Initialize the base pipeline
        
        Args:
            db: Database instance for storing data
            querier: Querier instance for fetching data
            processor: Processor instance for processing data
            batch_size: Number of transactions to process in a single batch
        """
        self.db = db
        self.querier = querier
        self.processor = processor
        self.batch_size = batch_size
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def fetch_data(self, start_timestamp, end_timestamp, skip):
        """Abstract method for fetching data from the DEX."""
        pass

    def process_batch(self, start_timestamp, end_timestamp, skip, max_retries=3, retry_delay=5):
        """
        Process a single batch of transactions.
        
        Args:
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            skip: Offset for pagination
            max_retries: Maximum number of retries
            retry_delay: Delay between retries
            
        Returns:
            tuple[bool, int, int, int]: has_more, transactions_processed, events_processed, next_skip
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Fetch data
                raw_data = self.fetch_data(start_timestamp, end_timestamp, skip)
                transactions = raw_data.get("data", {}).get("transactions", [])
                
                if not transactions:
                    logger.info(f"No transactions found for skip={skip}")
                    return False, 0, 0, skip

                # Process transactions
                processed_events = self.processor.process_bulk_responses(raw_data)
                total_events = sum(len(events) for events in processed_events)

                # Store processed events in the database
                self.db.insert_transaction_batch(processed_events)

                # Determine if more transactions remain
                has_more = len(transactions) >= self.batch_size
                next_skip = skip + len(transactions)

                logger.info(
                    f"Processed batch: {len(transactions)} transactions, {total_events} events, Skip: {skip}"
                )
                return has_more, len(transactions), total_events, next_skip

            except Exception as e:
                retry_count += 1
                logger.warning(
                    f"Retry {retry_count}/{max_retries} after error: {e}. Waiting {retry_delay} seconds..."
                )
                if retry_count >= max_retries:
                    logger.error(f"Failed to process batch after {max_retries} attempts. Skip: {skip}, Error: {e}")
                    raise
                time.sleep(retry_delay)

    def process_time_range(self, start_time, end_time):
        """
        Process data for a specific time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            dict: Statistics about the processed data
        """
        total_transactions, total_events = 0, 0
        skip = 0

        logger.info(f"Processing data from {start_time} to {end_time}")

        while True:
            has_more, batch_tx, batch_events, next_skip = self.process_batch(
                start_time, end_time, skip
            )
            total_transactions += batch_tx
            total_events += batch_events
            skip = next_skip

            if not has_more:
                break

        logger.info(
            f"Completed processing: {total_transactions} transactions, {total_events} events"
        )
        return {
            "transactions_processed": total_transactions,
            "events_processed": total_events,
        }
