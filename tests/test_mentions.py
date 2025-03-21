import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.models.user import get_user_id
from src.chat.models.message import send_channel_message, get_user_mentions
from src.chat.models.community import (
    get_community_id, get_channel_id, join_community
)
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()

class TestMentions(TestChatBase):
    def test_paul_mentions_spicelover(self):
        """paul tags spicelover"""
        paul_id = get_user_id("Paul")
        worms_id = get_channel_id("Worms")
        arrakis_id = get_community_id("Arrakis")
        
        # Send mention
        join_community(paul_id, arrakis_id)
        result = send_channel_message(paul_id, worms_id, "@spicelover test mention")
        self.assertTrue(result['sent'])
        
        # Check mentions
        mentions = get_user_mentions(get_user_id("spicelover"))
        self.assertTrue(any("@spicelover" in msg['message_content'] for msg in mentions))
        
        # Verify mention in database
        mention = exec_get_one("""
            SELECT mt.mentioned_user_id, m.message_content
            FROM mentions mt
            JOIN messages m ON mt.message_id = m.message_id
            WHERE mt.mentioned_user_id = %s
        """, (get_user_id("spicelover"),))
        self.assertIsNotNone(mention)
        self.assertIn("@spicelover", mention[1])

    def test_moe_mentions_spicelover_in_comedy(self):
        """moe tries to tag spicelover"""
        moe_id = get_user_id("m03")
        argument_clinic_id = get_channel_id("ArgumentClinic")
        
        # Send mention
        message_result = send_channel_message(
            moe_id,
            argument_clinic_id,
            "@spicelover, look what we have here!"
        )
        self.assertTrue(message_result['sent'])
        
        # Check mentions
        mentions = get_user_mentions(get_user_id("spicelover"))
        self.assertFalse(any("great argument" in msg['message_content'] for msg in mentions))
        
        # Verify no mention in database
        mention = exec_get_one("""
            SELECT COUNT(*) FROM mentions mt
            JOIN messages m ON mt.message_id = m.message_id
            WHERE mt.mentioned_user_id = %s AND m.message_content LIKE '%%great argument%%'
        """, (get_user_id("spicelover"),))
        self.assertEqual(mention[0], 0)

if __name__ == '__main__':
    unittest.main()