from typing import List

class PostgresSchema:
    @staticmethod
    def get_schema_queries() -> List[str]:
        return [
            # Extension for better timestamp handling
            "CREATE EXTENSION IF NOT EXISTS btree_gist",
            
            # Base transactions table with time-based partitioning
            '''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                dex_id TEXT NOT NULL,
                block_number BIGINT,
                timestamp TIMESTAMPTZ NOT NULL,
                gas_used NUMERIC,
                gas_price NUMERIC
            ) PARTITION BY RANGE (timestamp)
            ''',
            
            # Create partitions (example)
            '''
            CREATE TABLE transactions_2024_q1 PARTITION OF transactions
            FOR VALUES FROM ('2024-01-01') TO ('2024-04-01')
            ''',
            
            # Swaps table with partitioning
            '''
            CREATE TABLE IF NOT EXISTS swaps (
                id TEXT PRIMARY KEY,
                transaction_id TEXT REFERENCES transactions(id),
                dex_id TEXT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                pool_id TEXT,
                token0_symbol TEXT,
                token1_symbol TEXT,
                token0_decimals INTEGER,
                token1_decimals INTEGER,
                fee_tier INTEGER,
                liquidity NUMERIC,
                sqrt_price NUMERIC,
                token0_price NUMERIC,
                token1_price NUMERIC,
                sender TEXT,
                recipient TEXT,
                origin TEXT,
                amount0 NUMERIC,
                amount1 NUMERIC,
                amount_usd NUMERIC,
                sqrt_price_x96 NUMERIC,
                tick INTEGER,
                log_index INTEGER
            ) PARTITION BY RANGE (timestamp)
            ''',
            
            # Indexes optimized for time-series queries
            '''
            CREATE INDEX IF NOT EXISTS idx_swaps_timestamp_brin 
            ON swaps USING BRIN (timestamp) WITH (pages_per_range = 32)
            ''',
            
            '''
            CREATE INDEX IF NOT EXISTS idx_swaps_dex_timestamp 
            ON swaps (dex_id, timestamp)
            ''',
            
            '''
            CREATE INDEX IF NOT EXISTS idx_swaps_tokens 
            ON swaps (token0_symbol, token1_symbol)
            '''
        ]
    
    @staticmethod
    def get_partition_query(table: str, start_date: str, end_date: str) -> str:
        return f'''
        CREATE TABLE IF NOT EXISTS {table} 
        PARTITION OF {table.split('_')[0]}
        FOR VALUES FROM ('{start_date}') TO ('{end_date}')
        '''