import unittest
import csv
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.models.message import import_chat_data
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()
 
class TestDataImport(TestChatBase):
    def test_csv_import(self):
        """importing chat logs"""
        # Create test CSV
        with open('tests/chat.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Sender', 'Message'])
            writer.writerow(['Abbott', "Who's on first?"])
            writer.writerow(['Costello', "That's what I want to find out!"])
        
        # Import data
        result = import_chat_data('tests/chat.csv')
        self.assertTrue(result['sent'])
        self.assertGreater(result['messages_imported'], 0)
        
        # Verify messages in database
        messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE message_content IN (%s, %s)
        """, ("Who's on first?", "That's what I want to find out!"))
        self.assertEqual(messages[0], 2)
        
if __name__ == '__main__':
    unittest.main()