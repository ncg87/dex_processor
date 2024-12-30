from typing import Dict, Any
from datetime import timedelta
import dotenv
class Settings:
    POSTGRES_CONFIG = dotenv.get_key('.env', 'POSTGRES_CONFIG')
    BATCH_SIZE = 1000
    
    # Time-based partition settings
    PARTITION_INTERVAL = timedelta(days=90)  # 3-month partitions
    
    # Query optimization settings
    MAX_QUERY_INTERVAL = timedelta(days=30)  # Maximum time range for a single query
    DEFAULT_QUERY_LIMIT = 1000
    
    API_KEY = dotenv.get_key('.env', 'API_KEY')
