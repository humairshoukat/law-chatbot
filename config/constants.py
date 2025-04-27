import os
import logging
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Validate environment variables
def validate_env():
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "OLLAMA_URL", "OLLAMA_MODEL"]
    for var in required_vars:
        if not os.getenv(var):
            logging.error(f"Environment variable {var} is missing.")
            raise EnvironmentError(f"Environment variable {var} is required but not set.")

validate_env()

# Neo4j configurations
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# OLLAMA configurations
OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")