import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .models import BaseTransaction, SwapEvent
from .schema import PostgresSchema

class Database:
    def __init__(self, connection_params: Dict[str, str]):
        self.connection_params = connection_params
        self._initialize_database()
    
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.connection_params)
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_database(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for query in PostgresSchema.get_schema_queries():
                    cur.execute(query)
            conn.commit()
    
    def ensure_partitions(self, start_date: datetime, end_date: datetime):
        """Ensure partitions exist for the given date range"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                current = start_date
                while current < end_date:
                    partition_start = current.strftime('%Y-%m-%d')
                    current += timedelta(days=90)  # 3-month partitions
                    partition_end = current.strftime('%Y-%m-%d')
                    
                    for table in ['transactions', 'swaps', 'mints', 'burns', 'flashed', 'collects']:
                        partition_name = f"{table}_{partition_start.replace('-', '_')}"
                        query = PostgresSchema.get_partition_query(
                            partition_name, partition_start, partition_end
                        )
                        cur.execute(query)
            conn.commit()
    
    def insert_transaction_batch(self, transactions: List[tuple[BaseTransaction, Dict[str, list]]]):
        """Batch insert transactions and their events"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Prepare transaction data
                tx_data = [(
                    tx.id, tx.dex_id, tx.block_number,
                    datetime.fromtimestamp(tx.timestamp),
                    tx.gas_used, tx.gas_price
                ) for tx, _ in transactions]
                
                # Batch insert transactions
                psycopg2.extras.execute_values(
                    cur,
                    '''
                    INSERT INTO transactions (
                        id, dex_id, block_number, timestamp, gas_used, gas_price
                    ) VALUES %s
                    ''',
                    tx_data
                )
                
                # Batch insert events
                for tx, events in transactions:
                    for event_type, event_list in events.items():
                        if event_list:
                            self._batch_insert_events(cur, event_type, event_list)
            
            conn.commit()
    
    def query_by_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        dex_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        token_pair: Optional[tuple[str, str]] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, List[Dict]]:
        """
        Enhanced query support with pagination and token filtering
        """
        event_types = event_types or ['swaps', 'mints', 'burns', 'flashed', 'collects']
        result = {}
        
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for event_type in event_types:
                    query = f'''
                    SELECT *
                    FROM {event_type}
                    WHERE timestamp >= %s AND timestamp <= %s
                    '''
                    params = [start_time, end_time]
                    
                    if dex_id:
                        query += ' AND dex_id = %s'
                        params.append(dex_id)
                    
                    if token_pair and event_type == 'swaps':
                        query += '''
                        AND (
                            (token0_symbol = %s AND token1_symbol = %s)
                            OR 
                            (token0_symbol = %s AND token1_symbol = %s)
                        )
                        '''
                        params.extend([token_pair[0], token_pair[1], token_pair[1], token_pair[0]])
                    
                    query += ' ORDER BY timestamp ASC LIMIT %s OFFSET %s'
                    params.extend([limit, offset])
                    
                    cur.execute(query, params)
                    result[event_type] = cur.fetchall()
        
        return result
    
    def get_statistics(
        self,
        start_time: datetime,
        end_time: datetime,
        dex_id: Optional[str] = None,
        interval: str = '1 hour'
    ) -> List[Dict]:
        """
        Get time-based statistics using window functions
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = '''
                WITH time_buckets AS (
                    SELECT
                        time_bucket(%s, timestamp) AS bucket,
                        dex_id,
                        COUNT(*) as num_transactions,
                        SUM(ABS(amount_usd::numeric)) as total_volume,
                        AVG(ABS(amount_usd::numeric)) as avg_transaction_size
                    FROM swaps
                    WHERE timestamp >= %s AND timestamp <= %s
                '''
                
                params = [interval, start_time, end_time]
                
                if dex_id:
                    query += ' AND dex_id = %s'
                    params.append(dex_id)
                
                query += '''
                    GROUP BY bucket, dex_id
                )
                SELECT
                    bucket,
                    dex_id,
                    num_transactions,
                    total_volume,
                    avg_transaction_size,
                    total_volume - LAG(total_volume) OVER (
                        PARTITION BY dex_id ORDER BY bucket
                    ) as volume_change
                FROM time_buckets
                ORDER BY bucket ASC
                '''
                
                cur.execute(query, params)
                return cur.fetchall()