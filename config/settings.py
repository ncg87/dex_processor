from typing import Dict, Any
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    POSTGRES_CONFIG = {
        "dbname": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD'),
        "host": os.getenv('DB_HOST'),
        "port": int(os.getenv('DB_PORT')) if os.getenv('DB_PORT') else 5432,
    }
    BATCH_SIZE = 1000
    
    DEXES = os.getenv('DEXES').split(',')
    
    # Time-based partition settings
    PARTITION_INTERVAL = timedelta(days=90)  # 3-month partitions
    
    # Query optimization settings
    MAX_QUERY_INTERVAL = timedelta(days=30)  # Maximum time range for a single query
    DEFAULT_QUERY_LIMIT = 1000
    QUERY_INTERVAL=os.getenv('QUERY_INTERVAL')
    MAX_CONCURRENT_QUERIES=os.getenv('MAX_CONCURRENT_QUERIES')

    # TheGraph API Key
    API_KEY = os.getenv('API_KEY')
    
    
