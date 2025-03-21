import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.database import rebuildTables, check_database_seed

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()

class TestDatabase(TestChatBase):
    def test_database_seed(self):
        """check if tables got data"""
        tables = check_database_seed()
        for table in tables:
            self.assertGreater(len(table), 0)
            
        # Validate specific test data exists
        message_content = exec_get_one(
            "SELECT COUNT(*) FROM messages WHERE message_content IN ('please reply', 'i replied already!')"
        )
        self.assertEqual(message_content[0], 2, "Required test messages not found")

if __name__ == '__main__':
    unittest.main()