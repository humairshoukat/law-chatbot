import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from pathlib import Path
from src.database.import_laws_to_neo4j import (
    clear_database, 
    create_law_node, 
    create_parent_child_relation, 
    create_sibling_relation,
    create_refers_to_relation,
    parse_docx,
    extract_metadata_from_filename,
    main
)

class TestImportLawsToNeo4j(unittest.TestCase):
    def test_extract_metadata_from_filename(self):
        # Test extracting metadata from filename
        filename = "CivilLaw_2020_SourceA.docx"
        book, year, source = extract_metadata_from_filename(filename)
        
        self.assertEqual(book, "CivilLaw")
        self.assertEqual(year, "2020")
        self.assertEqual(source, "SourceA")
        
        # Test with different filename format
        filename = "PanelCode_2019_SourceB.docx"
        book, year, source = extract_metadata_from_filename(filename)
        
        self.assertEqual(book, "PanelCode")
        self.assertEqual(year, "2019")
        self.assertEqual(source, "SourceB")
    
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    def test_clear_database(self, mock_neo4j):
        # Setup mock connection
        mock_conn = MagicMock()
        
        # Call the function
        clear_database(mock_conn)
        
        # Verify the query was executed
        mock_conn.query.assert_called_once_with("MATCH (n) DETACH DELETE n")
        
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    def test_create_law_node(self, mock_neo4j):
        # Setup mock connection
        mock_conn = MagicMock()
        
        # Call the function
        create_law_node(
            mock_conn, 
            "1.2", 
            "This is a test law", 
            "TestBook", 
            "2023", 
            "TestSource"
        )
        
        # Verify the query was executed with correct parameters
        mock_conn.query.assert_called_once()
        args, kwargs = mock_conn.query.call_args
        self.assertIn("MERGE (l:Law {number: $number", args[0])
        self.assertEqual(kwargs["parameters"]["number"], "1.2")
        self.assertEqual(kwargs["parameters"]["text"], "This is a test law")
        self.assertEqual(kwargs["parameters"]["book"], "TestBook")
        self.assertEqual(kwargs["parameters"]["year"], "2023")
        self.assertEqual(kwargs["parameters"]["source"], "TestSource")
        
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    def test_create_parent_child_relation(self, mock_neo4j):
        # Setup mock connection
        mock_conn = MagicMock()
        
        # Call the function
        create_parent_child_relation(mock_conn, "1", "1.1")
        
        # Verify the query was executed with correct parameters
        mock_conn.query.assert_called_once()
        args, kwargs = mock_conn.query.call_args
        self.assertIn("MATCH (parent:Law {number: $parent_number})", args[0])
        self.assertIn("MATCH (child:Law {number: $child_number})", args[0])
        self.assertIn("MERGE (parent)-[:HAS_CHILD]->(child)", args[0])
        self.assertEqual(kwargs["parameters"]["parent_number"], "1")
        self.assertEqual(kwargs["parameters"]["child_number"], "1.1")
        
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    def test_create_sibling_relation(self, mock_neo4j):
        # Setup mock connection
        mock_conn = MagicMock()
        
        # Call the function
        create_sibling_relation(mock_conn, "1.1", "1.2")
        
        # Verify the query was executed with correct parameters
        mock_conn.query.assert_called_once()
        args, kwargs = mock_conn.query.call_args
        self.assertIn("MATCH (a:Law {number: $first_number})", args[0])
        self.assertIn("MATCH (b:Law {number: $second_number})", args[0])
        self.assertIn("MERGE (a)-[:NEXT_SIBLING]->(b)", args[0])
        self.assertEqual(kwargs["parameters"]["first_number"], "1.1")
        self.assertEqual(kwargs["parameters"]["second_number"], "1.2")
        
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    def test_create_refers_to_relation(self, mock_neo4j):
        # Setup mock connection
        mock_conn = MagicMock()
        
        # Call the function
        create_refers_to_relation(mock_conn, "1.1", "2.3")
        
        # Verify the query was executed with correct parameters
        mock_conn.query.assert_called_once()
        args, kwargs = mock_conn.query.call_args
        self.assertIn("MATCH (a:Law {number: $from_number})", args[0])
        self.assertIn("MATCH (b:Law {number: $to_number})", args[0])
        self.assertIn("MERGE (a)-[:REFERS_TO]->(b)", args[0])
        self.assertEqual(kwargs["parameters"]["from_number"], "1.1")
        self.assertEqual(kwargs["parameters"]["to_number"], "2.3")
        
    @patch('src.database.import_laws_to_neo4j.Document')
    def test_parse_docx(self, mock_document):
        # Setup mock document with paragraphs
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance
        
        # Create mock paragraphs with law text
        mock_paragraphs = [
            MagicMock(text="1. Introduction to Law"),
            MagicMock(text="1.1. Definition of Law"),
            MagicMock(text="1.2. Sources of Law"),
            MagicMock(text="This is not a section header"),
            MagicMock(text="2. Legal Systems"),
            MagicMock(text=""),  # Empty paragraph
        ]
        mock_doc_instance.paragraphs = mock_paragraphs
        
        # Call the function
        results = parse_docx("dummy_path.docx", "dummy_filename.docx")
        
        # Verify results
        expected_results = [
            ("1", "Introduction to Law"),
            ("1.1", "Definition of Law"),
            ("1.2", "Sources of Law"),
            ("2", "Legal Systems"),
        ]
        self.assertEqual(results, expected_results)
        
    @patch('src.database.import_laws_to_neo4j.Neo4jConnection')
    @patch('src.database.import_laws_to_neo4j.os.listdir')
    @patch('src.database.import_laws_to_neo4j.parse_docx')
    @patch('src.database.import_laws_to_neo4j.extract_metadata_from_filename')
    def test_main_function(self, mock_extract, mock_parse, mock_listdir, mock_neo4j):
        # Setup mocks
        mock_conn = MagicMock()
        mock_neo4j.return_value.__enter__.return_value = mock_conn
        
        mock_listdir.return_value = ["CivilLaw_2020_SourceA.docx"]
        mock_extract.return_value = ("CivilLaw", "2020", "SourceA")
        mock_parse.return_value = [
            ("1", "Introduction"),
            ("1.1", "Definition"),
            ("1.1.1", "Historical context"),
            ("1.2", "Applications"),
            ("2", "Legal Framework")
        ]
        
        # Call main function
        main()
        
        # Verify database was cleared
        mock_conn.query.assert_any_call("MATCH (n) DETACH DELETE n")
        
        # Verify nodes were created
        self.assertEqual(mock_conn.query.call_count, 11)  # 1 Clear + 5 nodes + 3 parent-child + 2 sibling
        
        # Count number of each type of query
        node_creation_count = 0
        parent_child_count = 0
        sibling_count = 0
        
        # Count call types by examining the queries
        for call in mock_conn.query.call_args_list:
            args, kwargs = call
            query = args[0]
            if "MERGE (l:Law" in query:
                node_creation_count += 1
            elif "MERGE (parent)-[:HAS_CHILD]->(child)" in query:
                parent_child_count += 1
            elif "MERGE (a)-[:NEXT_SIBLING]->(b)" in query:
                sibling_count += 1
                
        # Verify counts of each query type
        self.assertEqual(node_creation_count, 5)  # One for each section
        self.assertEqual(parent_child_count, 3)   # For 1.1, 1.1.1, and 1.2
        self.assertEqual(sibling_count, 2)        # Between siblings at same level
        
if __name__ == '__main__':
    unittest.main()
