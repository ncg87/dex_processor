import logging
import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values, RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .models import Token
from .schema import PostgresSchema

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config: Dict[str, Any]):
        """Initialize database connection"""
        self.config = config
        self.schema = PostgresSchema()
        self.ensure_database_exists()
        self._init_db()
        logger.info("Database initialized")

    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(**self.config)

    def _init_db(self):
        """Initialize database schema"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Execute schema creation queries
                    for query in self.schema.get_schema_queries():
                        cur.execute(query)
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database schema: {str(e)}", exc_info=True)
            raise
    
    def ensure_database_exists(self):
        """Ensure the database exists, create it if it doesn't"""
        # Connect to default postgres database
        config = self.config.copy()
        
        target_db = config.pop('dbname', None)
        config['dbname'] = 'postgres'  # Connect to default database
        
        try:
            # Need to connect with autocommit for database creation
            conn = psycopg2.connect(**config)
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                # Check if database exists
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s",
                        (target_db,))
                if not cur.fetchone():
                    # Create database if it doesn't exist
                    cur.execute(f"CREATE DATABASE {target_db}")
                    logger.info(f"Created database {target_db}")
        except Exception as e:
            logger.error(f"Error ensuring database exists: {str(e)}", exc_info=True)
            raise
    
    def ensure_partitions(self, start_date: datetime, end_date: datetime):
        """Ensure partitions exist for the given date range"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    queries = self.schema.get_partition_queries(
                        start_date,
                        end_date + timedelta(days=1),  # Include end date
                        timedelta(days=30)  # Monthly partitions
                    )
                    for query in queries:
                        cur.execute(query)
            logger.debug(f"Ensured partitions exist from {start_date} to {end_date}")
        except Exception as e:
            logger.error(f"Error ensuring partitions: {str(e)}", exc_info=True)
            raise
    
    # TODO: Make an separate function for inserting events, so that it can be used for other pipelines as well
    # Make a seperate file for the DB operations
    
    def insert_transaction_batch(self, events_list: List[List]):
        """
        Insert a batch of events into their respective tables
        
        Args:
            events_list: List containing lists of events [swaps, mints, burns, collects, flashs]
        """
        try:
            # Extract timestamps from the batch
            timestamps = [event.timestamp for events in events_list for event in events if events]
            if timestamps:
            # Determine the date range of the batch
                start_date = datetime.utcfromtimestamp(min(timestamps))
                end_date = datetime.utcfromtimestamp(max(timestamps))
                self.ensure_partitions(start_date, end_date)  # Ensure partitions exist for the range
            # Insert events
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert each type of event
                    self._batch_insert_events(cur, events_list)
                    
            logger.debug(f"Successfully inserted batch of events")
        except Exception as e:
            logger.error(f"Error inserting transaction batch: {str(e)}", exc_info=True)
            raise

    def _batch_insert_events(self, cur, events_list: List[List]):
        """
        Insert events in batch
        
        Args:
            cur: Database cursor
            events_list: List containing lists of events [swaps, mints, burns, collects, flashs]
        """
        logging.debug(f"Prepared {sum(len(events) for events in events_list)} transactions for insertion")
        try:
            # Get the events from the list
            swaps, mints, burns, collects, flashs = events_list
            logging.debug("Executing batch insert with SQL: ...")
            
            # Helper function to collect token metadata
            def collect_token_metadata(events):
                metadata = set()
                for event in events:
                    metadata.add((event.token0_id, event.token0_symbol, event.token0_name))
                    metadata.add((event.token1_id, event.token1_symbol, event.token1_name))
                return metadata
            
            # Collect token metadata from all event types
            token_metadata = set()
            for event_list in [swaps, mints, burns]:
                token_metadata.update(collect_token_metadata(event_list))
            
            # Insert swaps
            if swaps:
                swap_values = [
                    (
                        swap.id,
                        psycopg2.extras.Json(swap.parent_transaction.__dict__),
                        swap.timestamp,
                        swap.dex_id,
                        swap.token0_symbol,
                        swap.token1_symbol,
                        swap.token0_id,
                        swap.token1_id,
                        swap.token0_name,
                        swap.token1_name,
                        swap.amount0,
                        swap.amount1,
                        swap.amount_usd,
                        swap.sender,
                        swap.recipient,
                        swap.origin,
                        swap.fee_tier,
                        swap.liquidity
                        ) for swap in swaps if swap.amount0 is not None or swap.amount1 is not None
                    ]
                execute_values(
                    cur,
                    """
                    INSERT INTO swaps (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, token0_id, token1_id,
                        token0_name, token1_name,
                        amount0, amount1, amount_usd, sender, recipient, origin,
                        fee_tier, liquidity
                    ) VALUES %s
                    ON CONFLICT (timestamp, id) DO NOTHING;
                    """,
                    swap_values
                )
            
            # Insert mints
            if mints:
                mint_values = [
                    (
                        mint.id,
                        psycopg2.extras.Json(mint.parent_transaction.__dict__),
                        mint.timestamp,
                        mint.dex_id,
                        mint.token0_symbol,
                        mint.token1_symbol,
                        mint.token0_id,
                        mint.token1_id,
                        mint.token0_name,
                        mint.token1_name,
                        mint.amount0,
                        mint.amount1,
                        mint.amount_usd,
                        mint.owner,
                        mint.origin,
                        mint.fee_tier,
                        mint.liquidity
                    ) for mint in mints if mint.amount0 is not None or mint.amount1 is not None
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO mints (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, token0_id, token1_id,
                        token0_name, token1_name,
                        amount0, amount1, amount_usd, owner, origin,
                        fee_tier, liquidity
                    ) VALUES %s
                    ON CONFLICT (timestamp, id) DO NOTHING
                    """,
                    mint_values
                )
            
            # Insert burns
            if burns:
                burn_values = [
                    (
                        burn.id,
                        psycopg2.extras.Json(burn.parent_transaction.__dict__),
                        burn.timestamp,
                        burn.dex_id,
                        burn.token0_symbol,
                        burn.token1_symbol,
                        burn.token0_id,
                        burn.token1_id,
                        burn.token0_name,
                        burn.token1_name,
                        burn.amount0,
                        burn.amount1,
                        burn.amount_usd,
                        burn.owner,
                        burn.origin,
                        burn.fee_tier,
                        burn.liquidity
                    ) for burn in burns if burn.amount0 is not None or burn.amount1 is not None
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO burns (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, token0_id, token1_id,
                        token0_name, token1_name,
                        amount0, amount1, amount_usd, owner, origin,
                        fee_tier, liquidity
                    ) VALUES %s
                    ON CONFLICT (timestamp, id) DO NOTHING
                    """,
                    burn_values
                )
                
            # Note: Collect and Flash events are currently passed as empty lists
            # Add implementation when needed
            
            # Insert token metadata
            if token_metadata:
                self.insert_token_metadata(list(token_metadata))

        except Exception as e:
            logger.error(f"Error in batch insert: {str(e)}", exc_info=True)
            raise

    def insert_token_metadata(self, tokens: List[tuple]):
        """
        Insert token metadata.

        Args:
            tokens: List of tuples containing token metadata (id, symbol, name).
        
        """
        insert_query = """
        INSERT INTO token_metadata (id, symbol, name)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
        RETURNING id
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Execute batch insertion and fetch the count of new tokens
                    execute_values(cur, insert_query, tokens)
                    cur.execute("SELECT COUNT(*) FROM token_metadata WHERE id IN %s", (tuple(t[0] for t in tokens),))
                    new_tokens = cur.fetchall()
                    conn.commit()
                    logger.debug(f"Inserted {new_tokens} new tokens into token_metadata.")
        except Exception as e:
            logger.error(f"Error inserting token metadata: {str(e)}", exc_info=True)
            raise
        
    def get_events_by_time(
        self,
        event_type: str,
        start_time: int,  # UNIX timestamp
        end_time: int,    # UNIX timestamp
        dex_id: str = None,
    ) -> List[Dict]:
        """
        Fetch events of a given type within a specified time range.
        """
        query = f"""
            SELECT *
            FROM {event_type}
            WHERE timestamp >= %s AND timestamp <= %s
        """
        params = [start_time, end_time]

        if dex_id:
            query += " AND dex_id = %s"
            params.append(dex_id)

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Error fetching events from {event_type}: {str(e)}", exc_info=True)
            raise
    
    def get_all_tokens(self) -> list:
        """
        Retrieve all tokens from the database.
        """
        query = "SELECT * FROM token_metadata"
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    tokens = cur.fetchall()
            return [dict(token) for token in tokens]
        except Exception as e:
            logger.error(f"Error fetching tokens: {str(e)}", exc_info=True)
            raise
        
    def get_tokens_by_symbol(self, symbol: str) -> list:
        """
        Retrieve tokens filtered by symbol.
        """
        query = "SELECT * FROM tokens WHERE symbol = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (symbol,))
                    tokens = cur.fetchall()
            return [dict(token) for token in tokens]
        except Exception as e:
            logger.error(f"Error fetching tokens by symbol: {str(e)}", exc_info=True)
            raise
    def get_token_by_id(self, token_id: str) -> list:
        """
        Retrieve a token by its ID.
        """
        query = "SELECT * FROM token_metadata WHERE id = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (token_id,))
                    tokens = cur.fetchall()
                    return [dict(token) for token in tokens]
        except Exception as e:
            logger.error(f"Error fetching token by ID: {str(e)}", exc_info=True)
            raise
    from datetime import datetime, timedelta

    def get_crypto_events_by_time(
        self, 
        event_type: str, 
        start_time: int, 
        end_time: int, 
        crypto_id: str = None
    ) -> list:
        """
        Retrieve events of a specific cryptocurrency within a specified time range.
        Args:
            event_type: The type of events (e.g., 'swaps', 'mints', 'burns').
            crypto_id: The ID of the cryptocurrency (optional).
            start_time: The start time as a UNIX timestamp.
            end_time: The end time as a UNIX timestamp.
        Returns:
            List of events involving the specified cryptocurrency or all events if no crypto_id is provided.
        """
        if crypto_id:
            query = f"""
                SELECT *
                FROM {event_type}
                WHERE (token0_id = %s OR token1_id = %s)
                AND timestamp >= %s AND timestamp <= %s
            """
            params = [crypto_id, crypto_id, start_time, end_time]
        else:
            query = f"""
                SELECT *
                FROM {event_type}
                WHERE timestamp >= %s AND timestamp <= %s
            """
            params = [start_time, end_time]

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()
        except Exception as e:
            logger.error(
                f"Error fetching events for event type {event_type} and crypto ID {crypto_id or 'ALL'}: {str(e)}",
                exc_info=True
            )
            raise





