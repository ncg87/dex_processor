import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

@contextmanager
def get_db_connection(config):
    conn = psycopg2.connect(**config)
    try:
        yield conn
    finally:
        conn.close()

def execute_query(conn, query, params=None):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchall()
