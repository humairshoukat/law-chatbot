"""
This module handles importing laws from .docx files into the Neo4j database.

Functions:
- clear_database: Clears all nodes and relationships in the database.
- create_law_node: Creates a law node with metadata.
- create_parent_child_relation: Creates a parent-child relationship between laws.
- create_sibling_relation: Creates a sibling relationship between laws.
- create_refers_to_relation: Creates a reference relationship between laws.
- parse_docx: Parses a .docx file to extract law sections.
- extract_metadata_from_filename: Extracts metadata from the filename.
- main: Main function to orchestrate the import process.
"""

from docx import Document
from pathlib import Path
from src.database.neo4j_utils import Neo4jConnection
from config.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import os
import re

# Folder containing .docx files
DATA_DIR = Path(__file__).parents[2] / "data" / "laws"

def clear_database(conn):
    conn.query("MATCH (n) DETACH DELETE n")

def create_law_node(conn, section_number, text, book, year, source):
    conn.query(
        """
        MERGE (l:Law {number: $number, book: $book, year: $year, source: $source})
        SET l.text = $text
        """,
        parameters={"number": section_number, "text": text, "book": book, "year": year, "source": source}
    )

def create_parent_child_relation(conn, parent_number, child_number):
    conn.query(
        """
        MATCH (parent:Law {number: $parent_number})
        MATCH (child:Law {number: $child_number})
        MERGE (parent)-[:HAS_CHILD]->(child)
        """,
        parameters={"parent_number": parent_number, "child_number": child_number}
    )

def create_sibling_relation(conn, first_number, second_number):
    conn.query(
        """
        MATCH (a:Law {number: $first_number})
        MATCH (b:Law {number: $second_number})
        MERGE (a)-[:NEXT_SIBLING]->(b)
        """,
        parameters={"first_number": first_number, "second_number": second_number}
    )

def create_refers_to_relation(conn, from_number, to_number):
    conn.query(
        """
        MATCH (a:Law {number: $from_number})
        MATCH (b:Law {number: $to_number})
        MERGE (a)-[:REFERS_TO]->(b)
        """,
        parameters={"from_number": from_number, "to_number": to_number}
    )

def parse_docx(filepath, filename):
    document = Document(filepath)
    lines = []
    for para in document.paragraphs:
        text = para.text.strip()
        if text:
            # Match things like '1.', '1.1.', '1.1.1.', followed by text
            match = re.match(r'^(\d+(\.\d+)*\.)\s+(.*)', text)
            if match:
                section_number = match.group(1).rstrip(".")  # remove trailing dot
                section_text = match.group(3)
                lines.append((section_number, section_text))
    return lines

def extract_metadata_from_filename(filename):
    parts = filename.replace(".docx", "").split("_")
    book = parts[0]
    year = parts[1]
    source = parts[2]
    return book, year, source

def main():
    with Neo4jConnection() as conn:
        print("✅ Connected to Neo4j")

        # Step 1: Clear database
        clear_database(conn)

        for filename in os.listdir(DATA_DIR):
            filepath = DATA_DIR / filename
            print(f"Processing {filename}")

            book, year, source = extract_metadata_from_filename(filename)
            sections = parse_docx(filepath, filename)
            print(f"Found {len(sections)} sections in {filename}")

            last_section_per_level = {}  # for siblings

            for idx, (section_number, section_text) in enumerate(sections):
                create_law_node(conn, section_number, section_text, book, year, source)

                # Handle Parent-Child
                parent_number = ".".join(section_number.split(".")[:-1])
                if parent_number:
                    create_parent_child_relation(conn, parent_number, section_number)

                # Handle Sibling
                level = section_number.count(".")
                if level in last_section_per_level:
                    previous_sibling = last_section_per_level[level]
                    create_sibling_relation(conn, previous_sibling, section_number)

                last_section_per_level[level] = section_number

            # Step 2: Handle internal references (See Section X.X)
            for section_number, section_text in sections:
                references = re.findall(r'See Section (\d+(\.\d+)*)', section_text)
                for ref_number, _ in references:
                    create_refers_to_relation(conn, section_number, ref_number)

    print("✅ Import complete!")

if __name__ == "__main__":
    main()