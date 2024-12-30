import os
import time
import logging
from datetime import datetime, timedelta
from pipelines import DataPipeline
import dotenv
from concurrent.futures import ThreadPoolExecutor


QUERY_INTERVAL = int(dotenv.get_key('.env', 'QUERY_INTERVAL', 300))
MAX_CONCURRENT_QUERIES = int(dotenv.get_key('.env', 'MAX_CONCURRENT_QUERIES', 5))

# Set up logging
logging.basicConfig(
    filename="pipeline_automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_pipeline(start_time, end_time):
    """Runs the pipeline for the specified time range."""
    logger.info(f"Starting pipeline execution for range {start_time} to {end_time}")
    dex_id = "uniswap_v3"
    pipeline = DataPipeline(dex_id)
    
    try:
        total_tx, total_events = pipeline.process_time_range(start_time, end_time)
        logger.info(
            f"Pipeline execution completed: {total_tx} transactions, {total_events} events."
        )
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)

def schedule_queries():
    """Schedules pipeline queries at regular intervals."""
    executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_QUERIES)
    next_start_time = datetime.now()

    while True:
        end_time = datetime.now()
        start_time = next_start_time
        next_start_time = end_time

        logger.info(f"Scheduling query for range {start_time} to {end_time}")
        executor.submit(run_pipeline, start_time, end_time)

        # Wait for the specified interval before scheduling the next query
        time.sleep(QUERY_INTERVAL)

if __name__ == "__main__":
    while True:
        run_pipeline()
        time.sleep(QUERY_INTERVAL)
