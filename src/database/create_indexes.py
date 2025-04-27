from src.database.neo4j_utils import Neo4jConnection
from config.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def create_indexes(conn):
    conn.query("CREATE INDEX law_number IF NOT EXISTS FOR (l:Law) ON (l.number)")
    conn.query("CREATE INDEX law_book IF NOT EXISTS FOR (l:Law) ON (l.book)")
    conn.query("CREATE INDEX law_year IF NOT EXISTS FOR (l:Law) ON (l.year)")
    conn.query("CREATE INDEX law_source IF NOT EXISTS FOR (l:Law) ON (l.source)")
    conn.query("CREATE INDEX law_text IF NOT EXISTS FOR (l:Law) ON (l.text)")
    print("✅ Indexes created.")

def main():
    with Neo4jConnection() as conn:
        create_indexes(conn)

if __name__ == "__main__":
    main()