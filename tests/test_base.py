import unittest
from datetime import datetime, date
from src.swen344_db_utils import (
    exec_commit, 
    exec_sql_file, 
    exec_get_one, 
    connect,
)
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    """Base test class for chat application tests"""
    
    def setUp(self):
        """Set up test environment
        Creates fresh database tables and loads test data for each test
        """
        # Create fresh tables
        exec_sql_file('src/chatschema.sql')
        # Load test data
        rebuildTables()

class TestPostgreSQL(unittest.TestCase):
    def test_can_connect(self):
        """Test PostgreSQL connection"""
        conn = connect()
        cur = conn.cursor()
        result = exec_get_one('SELECT VERSION()')
        self.assertTrue(result[0].startswith('PostgreSQL'))
        conn.close()

if __name__ == '__main__':
    unittest.main()