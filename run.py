import asyncio
import logging
from datetime import datetime, timedelta
from database import Database
from config.settings import Settings
from factory.pipeline_factory import PipelineFactory

logging.basicConfig(
    filename='maintenance.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

QUERY_INTERVAL = int(Settings.QUERY_INTERVAL)


async def run_pipeline(pipeline, start_time, end_time):
    """
    Run the pipeline for a given time range asynchronously
    """
    try:
        logger.info(f"Starting pipeline for {pipeline.__class__.__name__} from {start_time} to {end_time}")
        stats = await asyncio.to_thread(pipeline.process_time_range, start_time, end_time)
        logger.info(
            f"Pipeline completed: {stats['transactions_processed']} transactions, "
            f"{stats['events_processed']} events."
        )
    except Exception as e:
        logger.error(f"Error in pipeline {pipeline.__class__.__name__}: {e}", exc_info=True)

async def initial_query(pipelines):
    """
    Query data for the previous day for all pipelines
    """
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()
    logger.info(f"Starting initial query for the previous day: {start_time.date()} to {end_time.date()}")

    tasks = []
    for pipeline in pipelines.values():
        tasks.append(run_pipeline(pipeline, start_time, end_time))

    # Run all initial queries concurrently
    await asyncio.gather(*tasks)
    logger.info("Initial query completed.")

async def query_loop(pipelines):
    """
    Continuously query data at regular intervals
    """
    while True:
        start_time = datetime.now() - timedelta(seconds=QUERY_INTERVAL)
        end_time = datetime.now()

        tasks = []
        for pipeline in pipelines.values():
            tasks.append(run_pipeline(pipeline, start_time, end_time))

        # Run all pipelines concurrently
        await asyncio.gather(*tasks)

        logger.info(f"Sleeping for {QUERY_INTERVAL} seconds...")
        await asyncio.sleep(QUERY_INTERVAL)


async def main():
    try:
        # Initialize database
        db = Database(Settings.POSTGRES_CONFIG)

        # Load pipelines using the factory
        pipelines = PipelineFactory.load_pipelines(db)
        if not pipelines:
            logger.error("No pipelines loaded. Ensure DEXES are configured correctly.")
            return

        logger.info(f"Loaded pipelines for DEXes: {', '.join(pipelines.keys())}")

        # Run initial query for the previous day
        await asyncio.gather(
            initial_query(pipelines),
            query_loop(pipelines)
        )
        
    except KeyboardInterrupt:
        logger.warning("Received KeyboardInterrupt. Shutting down...") 

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
