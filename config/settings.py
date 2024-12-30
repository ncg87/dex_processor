from typing import Dict, Any
from datetime import timedelta
import dotenv
class Settings:
    POSTGRES_CONFIG = {
        "dbname": dotenv.get_key('.env', 'DB_NAME'),
        "user": dotenv.get_key('.env', 'DB_USER'),
        "password": dotenv.get_key('.env', 'DB_PASSWORD'),
        "host": dotenv.get_key('.env', 'DB_HOST'),
        "port": int(dotenv.get_key('.env', 'DB_PORT')),
}
    BATCH_SIZE = 1000
    
    # Time-based partition settings
    PARTITION_INTERVAL = timedelta(days=90)  # 3-month partitions
    
    # Query optimization settings
    MAX_QUERY_INTERVAL = timedelta(days=30)  # Maximum time range for a single query
    DEFAULT_QUERY_LIMIT = 1000
    
    API_KEY = dotenv.get_key('.env', 'API_KEY')
