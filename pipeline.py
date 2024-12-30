import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from database import Database
from factory.querier_factory import QuerierFactory
from factory.processor_factory import ProcessorFactory
from config.settings import Settings
from factory.pipeline_factory import PipelineFactory

logger = logging.getLogger(__name__)

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        db = Database(Settings.POSTGRES_CONFIG)
        
        # Initialize pipeline
        pipeline = PipelineFactory.get_pipeline('uniswap_v3', db)
        
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