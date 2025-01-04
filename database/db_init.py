class DBInitializer:
    def __init__(self, schema):
        self.schema = schema

    def init_db(self, conn):
        with conn.cursor() as cur:
            for query in self.schema.get_schema_queries():
                cur.execute(query)
