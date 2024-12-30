from database.database import Database
from config.settings import Settings
from datetime import datetime, timedelta
from pipelines import DataPipeline
import logging

logger = logging.getLogger(__name__)

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Database connection parameters
    db_params = {
        'dbname': 'your_db_name',
        'user': 'your_user',
        'password': 'your_password',
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        # Initialize pipeline
        pipeline = DataPipeline(db_params)
        
        # Process yesterday's data
        yesterday = datetime.now() - timedelta(days=1)
        total_tx, total_events = pipeline.process_day(yesterday)
        
        logger.info(
            f"Successfully processed {yesterday.date()}: "
            f"{total_tx} transactions, {total_events} events"
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()