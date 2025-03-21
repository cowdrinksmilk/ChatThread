import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.models.user import get_user_id
from src.chat.models.message import send_message
from src.chat.models.message_status import (
    count_unread_messages, mark_messages_as_read, count_direct_messages
)
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()
        
class TestMessageStatus(TestChatBase):
    def test_mark_message_read(self):
        """marking stuff as read"""
        abbott_id = get_user_id("ab0tt")
        costello_id = get_user_id("costell0")
        send_message(abbott_id, costello_id, "Test unread message")
        before_count = count_unread_messages(costello_id)
        self.assertGreater(before_count, 0)
        mark_messages_as_read(costello_id, abbott_id)
        after_count = count_unread_messages(costello_id)
        self.assertEqual(after_count, 0)
        
        # Verify database state
        unread = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE receiver_id = %s AND sender_id = %s AND NOT is_read
        """, (costello_id, abbott_id))
        self.assertEqual(unread[0], 0)

    def test_paul_moe_dm_count(self):
        """counting paul and moe's dms"""
        paul_id = get_user_id("Paul")
        moe_id = get_user_id("m03")
        dm_count = count_direct_messages(paul_id, moe_id)
        self.assertGreaterEqual(dm_count, 2)
        
        # Verify in database
        messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE ((sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s))
            AND is_direct_message = true
        """, (paul_id, moe_id, moe_id, paul_id))
        self.assertEqual(messages[0], dm_count)

if __name__ == '__main__':
    unittest.main()