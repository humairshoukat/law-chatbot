from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_indexes(tx):
    tx.run("CREATE INDEX law_number IF NOT EXISTS FOR (l:Law) ON (l.number)")
    tx.run("CREATE INDEX law_book IF NOT EXISTS FOR (l:Law) ON (l.book)")
    tx.run("CREATE INDEX law_year IF NOT EXISTS FOR (l:Law) ON (l.year)")
    tx.run("CREATE INDEX law_source IF NOT EXISTS FOR (l:Law) ON (l.source)")
    tx.run("CREATE INDEX law_text IF NOT EXISTS FOR (l:Law) ON (l.text)")
    print("✅ Indexes created.")

def main():
    with driver.session() as session:
        session.execute_write(create_indexes)

if __name__ == "__main__":
    main()