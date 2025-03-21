import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.models.user import get_user_id 
from src.chat.models.message import send_channel_message
from src.chat.models.message_status import get_user_unread_counts
from src.chat.models.community import (
    get_community_id, get_channel_id, join_community,
    check_community_membership
)
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()
        
class TestCommunity(TestChatBase):
    def test_paul_joins_arrakis(self):
        """paul joins the desert crew"""
        paul_id = get_user_id("Paul")
        arrakis_id = get_community_id("Arrakis")
        result = join_community(paul_id, arrakis_id)
        self.assertTrue(result['sent'])
        is_member = check_community_membership(paul_id, arrakis_id)
        self.assertTrue(is_member)
        
        # Verify membership in database
        membership = exec_get_one("""
            SELECT COUNT(*) FROM community_members 
            WHERE user_id = %s AND community_id = %s
        """, (paul_id, arrakis_id))
        self.assertEqual(membership[0], 1)

    def test_paul_message_to_worms(self):
        """paul chats about worms"""
        paul_id = get_user_id("Paul")
        spicelover_id = get_user_id("spicelover")
        worms_id = get_channel_id("Worms")
        arrakis_id = get_community_id("Arrakis")
        
        # Join and send message
        join_community(paul_id, arrakis_id)
        message_result = send_channel_message(paul_id, worms_id, "Test message")
        self.assertTrue(message_result['sent'])
        
        # Check unread counts
        unread = get_user_unread_counts(spicelover_id)
        self.assertEqual(unread['channel_unread'].get('Worms', 0), 1)
        
        # Verify message in database
        message = exec_get_one("""
            SELECT message_content, is_read, channel_id
            FROM messages 
            WHERE sender_id = %s AND channel_id = %s
        """, (paul_id, worms_id))
        self.assertEqual(message[0], "Test message")
        self.assertFalse(message[1])
        self.assertEqual(message[2], worms_id)

if __name__ == '__main__':
    unittest.main()