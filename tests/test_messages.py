import unittest
from datetime import datetime, date
from src.swen344_db_utils import exec_commit, exec_sql_file, exec_get_one

from src.chat.models.user import get_user_id
from src.chat.models.message import (
    send_message, get_messages_between_users, get_messages_on_specific_date,
    get_message_senders
)
from src.chat.database import rebuildTables

class TestChatBase(unittest.TestCase):
    def setUp(self):
        """quick db setup"""
        exec_sql_file('src/chatschema.sql')
        rebuildTables()

class TestMessages(TestChatBase):
    def test_send_message(self):
        """sending message test"""
        result = send_message(1, 2, "Hello, Costello!")
        self.assertTrue(result['sent'])
        self.assertEqual(result['message'], "Message sent")
        
        # Verify message in database
        message = exec_get_one(
            "SELECT message_content, is_read FROM messages WHERE sender_id = 1 AND receiver_id = 2 ORDER BY message_id DESC LIMIT 1"
        )
        self.assertEqual(message[0], "Hello, Costello!")
        self.assertFalse(message[1])

    def test_send_message_between_users(self):
        """checking if messages get through"""
        result = send_message(6, 7, "I'm doing the work, I'm baby-stepping")
        self.assertTrue(result['sent'])
        messages = get_messages_between_users(6, 7)
        self.assertTrue(any(
            msg['message_content'] == "I'm doing the work, I'm baby-stepping" 
            for msg in messages
        ))
        
        # Check database state
        message = exec_get_one("""
            SELECT message_content, is_read, is_direct_message 
            FROM messages 
            WHERE sender_id = 6 AND receiver_id = 7 
            ORDER BY message_id DESC LIMIT 1
        """)
        self.assertEqual(message[0], "I'm doing the work, I'm baby-stepping")
        self.assertFalse(message[1])
        self.assertTrue(message[2])

    def test_messages_between_abbott_and_costello(self):
        """checking abbott and costello's chat"""
        abbott_id = get_user_id("ab0tt")
        costello_id = get_user_id("costell0")
        result = get_messages_between_users(abbott_id, costello_id)
        self.assertGreater(len(result), 0)
        
        # Verify in database
        messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE (sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s)
        """, (abbott_id, costello_id, costello_id, abbott_id))
        self.assertEqual(messages[0], len(result))

    def test_messages_between_moe_and_larry_1995(self):
        """looking at moe and larry's old messages"""
        moe_id = get_user_id("m03")
        larry_id = get_user_id("l@rry")
        result = get_messages_between_users(
            moe_id, larry_id,
            start_date=date(1995, 1, 1),
            end_date=date(1995, 12, 31)
        )
        self.assertGreaterEqual(len(result), 0)
        
        # Verify dates in database
        if len(result) > 0:
            messages = exec_get_one("""
                SELECT COUNT(*) FROM messages 
                WHERE ((sender_id = %s AND receiver_id = %s)
                OR (sender_id = %s AND receiver_id = %s))
                AND timestamp BETWEEN %s AND %s
            """, (moe_id, larry_id, larry_id, moe_id, 
                  '1995-01-01', '1995-12-31'))
            self.assertEqual(messages[0], len(result))

    def test_get_messages_on_date(self):
        """grabbing messages from a specific day"""
        result = get_messages_on_specific_date('1953-09-23')
        self.assertGreater(len(result), 0)
        
        # Verify in database
        messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE DATE(timestamp) = %s::date
        """, ('1953-09-23',))
        self.assertEqual(messages[0], len(result))

    def test_get_message_senders(self):
        """who's been messaging?"""
        abbott_id = get_user_id("ab0tt")
        costello_id = get_user_id("costell0")
        send_message(costello_id, abbott_id, "Test message 1")
        send_message(costello_id, abbott_id, "Test message 2")
        senders = get_message_senders(abbott_id)
        self.assertGreater(len(senders), 0)
        self.assertTrue(all('unread_count' in s for s in senders))
        
        # Verify in database
        sender_count = exec_get_one("""
            SELECT COUNT(DISTINCT sender_id) 
            FROM messages 
            WHERE receiver_id = %s
        """, (abbott_id,))
        self.assertGreaterEqual(sender_count[0], 1)

    def test_historical_messages(self):
        """digging up some old chats"""
        abbott_id = get_user_id("ab0tt")
        costello_id = get_user_id("costell0")
        messages = get_messages_between_users(
            abbott_id, 
            costello_id,
            start_date="1922-01-01",
            end_date="1970-12-31"
        )
        self.assertGreater(len(messages), 0)
        
        # Verify date range in database
        db_messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE ((sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s))
            AND timestamp BETWEEN %s AND %s
        """, (abbott_id, costello_id, costello_id, abbott_id,
              '1922-01-01', '1970-12-31'))
        self.assertEqual(db_messages[0], len(messages))