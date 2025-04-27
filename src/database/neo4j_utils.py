"""
This module provides a utility class for interacting with the Neo4j database.

Classes:
- Neo4jConnection: Manages the connection to the Neo4j database and provides query execution methods.
"""

import logging
from neo4j import GraphDatabase
from config.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Neo4jConnection:
    def __init__(self):
        self.uri = NEO4J_URI
        self.user = NEO4J_USER
        self.password = NEO4J_PASSWORD
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        try:
            with self.driver.session() as session:
                return session.run(query, parameters)
        except Exception as e:
            logging.error(f"Error executing query: {query}, Error: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_write(self, func, *args, **kwargs):
        """
        Execute a write transaction with the given function and arguments.
        """
        try:
            with self.driver.session() as session:
                return session.write_transaction(func, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error executing write transaction: {e}")
            raise
