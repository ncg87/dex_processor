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
            logger.info(f"Ensured partitions exist from {start_date} to {end_date}")
        except Exception as e:
            logger.error(f"Error ensuring partitions: {str(e)}", exc_info=True)
            raise

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
                        swap.amount0,
                        swap.amount1,
                        swap.amount_usd,
                        swap.sender,
                        swap.recipient,
                        swap.origin,
                        swap.fee_tier,
                        swap.liquidity
                    ) for swap in swaps
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO swaps (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, amount0, amount1,
                        amount_usd, sender, recipient, origin,
                        fee_tier, liquidity
                    ) VALUES %s
                    ON CONFLICT (id) DO NOTHING;
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
                        mint.amount0,
                        mint.amount1,
                        mint.amount_usd,
                        mint.owner,
                        mint.origin,
                        mint.fee_tier,
                        mint.liquidity
                    ) for mint in mints
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO mints (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, amount0, amount1,
                        amount_usd, owner, origin, fee_tier, liquidity
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
                        burn.amount0,
                        burn.amount1,
                        burn.amount_usd,
                        burn.owner,
                        burn.origin,
                        burn.fee_tier,
                        burn.liquidity
                    ) for burn in burns
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO burns (
                        id, parent_transaction, timestamp, dex_id,
                        token0_symbol, token1_symbol, amount0, amount1,
                        amount_usd, owner, origin, fee_tier, liquidity
                    ) VALUES %s
                    ON CONFLICT (timestamp, id) DO NOTHING
                    """,
                    burn_values
                )
                
            # Note: Collect and Flash events are currently passed as empty lists
            # Add implementation when needed
            
        except Exception as e:
            logger.error(f"Error in batch insert: {str(e)}", exc_info=True)
            raise
    
    def upsert_token_metadata(self, tokens: List[Token]):
        """
        Insert or update token metadata.

        Args:
            tokens: List of Token objects with metadata (id, symbol, name).
        """
        insert_query = """
        INSERT INTO token_metadata (id, symbol, name)
        VALUES %s
        ON CONFLICT (id) DO UPDATE
        SET symbol = EXCLUDED.symbol,
            name = EXCLUDED.name,
            updated_at = CURRENT_TIMESTAMP;
        """
        # Prepare values for batch insertion
        values = [(token.id, token.symbol, token.name) for token in tokens]

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, insert_query, values)
                conn.commit()
                logger.info(f"Upserted {len(tokens)} tokens into token_metadata.")
        except Exception as e:
            logger.error(f"Error upserting token metadata: {str(e)}", exc_info=True)
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

