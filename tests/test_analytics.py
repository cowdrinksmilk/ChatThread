# tests/test_analytics.py
import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one
from src.chat.models.analytics import (
    search_messages,
    get_activity_summary,
    get_suspended_active_users
)
from src.chat.models.user import get_user_id
from src.chat.models.message import send_message, send_channel_message
from src.chat.models.community import get_channel_id
from src.chat.database import rebuildTables

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        rebuildTables()
        
        # Add specific test messages
        abbott_id = get_user_id("ab0tt")
        costello_id = get_user_id("costell0")
        
        # Only insert test messages once
        message_check = exec_get_one(
            "SELECT COUNT(*) FROM messages WHERE message_content IN ('please reply', 'i replied already!')"
        )
        if message_check[0] == 0:
            send_message(abbott_id, costello_id, "please reply")
            send_message(costello_id, abbott_id, "i replied already!")

        # Add channel messages for activity summary
        paul_id = get_user_id("Paul")
        worms_channel = get_channel_id("Worms")
        send_channel_message(paul_id, worms_channel, "Testing channel message 1")
        send_channel_message(paul_id, worms_channel, "Testing channel message 2")
        
    def test_search_single_term(self):
        """Test searching with a single term"""
        results = search_messages("reply")
        print("\nSearch results for 'reply':")
        for msg in results:
            print(f"{msg['sender']}: {msg['message_content']}")
            
        # Should find exactly 2 messages
        self.assertEqual(len(results), 2)
        messages = [msg['message_content'] for msg in results]
        self.assertIn("please reply", messages)
        self.assertIn("i replied already!", messages)
        
    def test_search_multiple_terms(self):
        """Test searching with multiple terms (AND)"""
        results = search_messages("reply please")
        print("\nSearch results for 'reply please':")
        for msg in results:
            print(f"{msg['sender']}: {msg['message_content']}")
            
        # Should find exactly 1 message
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['message_content'], "please reply")
        
    def test_activity_summary(self):
        """Test community activity metrics"""
        results = get_activity_summary('2024-02-15')
        print("\nActivity Summary:")
        for r in results:
            print(f"Community: {r['community']}")
            print(f"Avg Messages/Day: {r['avg_num_messages']}")
            print(f"Active Users: {r['active_users']}\n")
            
        self.assertTrue(len(results) > 0, "Should have activity data")
        first_community = results[0]
        self.assertIn('community', first_community)
        self.assertIn('avg_num_messages', first_community)
        self.assertIn('active_users', first_community)
        
    def test_suspended_users(self):
        """Test suspended users query"""
        # Ensure Paul's suspension exists
        paul_id = get_user_id("Paul")
        exec_commit("""
            INSERT INTO suspensions (user_id, community_id, start_date, end_date)
            SELECT %s, community_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '2 years'
            FROM communities WHERE name = 'Arrakis'
            ON CONFLICT DO NOTHING
        """, (paul_id,))
        
        results = get_suspended_active_users('2024-01-01', '2024-12-31')
        print("\nSuspended Users with Activity:")
        for r in results:
            print(f"User: {r['username']}")
            print(f"Suspended from: {r['suspended_from']}")
            print(f"Until: {r['end_date']}\n")
            
        # Paul should be in results for Arrakis suspension
        paul_suspension = next(
            (r for r in results 
             if r['username'] == 'Paul' and r['suspended_from'] == 'Arrakis'),
            None
        )
        self.assertIsNotNone(paul_suspension)
        
if __name__ == '__main__':
    unittest.main()