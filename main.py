from database.database import Database
from config.settings import Settings
from datetime import datetime, timedelta

def main():
    # Initialize database
    db = Database(Settings.POSTGRES_CONFIG)
    
    # Ensure partitions exist for the next year
    start_date = datetime.now()
    end_date = start_date + timedelta(days=365)
    db.ensure_partitions(start_date, end_date)
    
    # Example query with statistics
    stats = db.get_statistics(
        start_time=datetime.now() - timedelta(days=7),
        end_time=datetime.now(),
        dex_id='uniswap_v3',
        interval='1 hour'
    )
    
    # Example time-range query with token pair filtering
    swaps = db.query_by_timerange(
        start_time=datetime.now() - timedelta(hours=24),
        end_time=datetime.now(),
        dex_id='uniswap_v3',
        event_types=['swaps'],
        token_pair=('USDC', 'ETH'),
        limit=100
    )

if __name__ == "__main__":
    main()