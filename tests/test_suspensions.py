from src.swen344_db_utils import exec_get_one
from src.chat.models.user import get_user_id
from src.chat.models.message import send_message, send_channel_message
from src.chat.models.community import (
    get_community_id, get_channel_id, join_community
)
from src.chat.models.suspension import suspend_user_from_community
from .test_base import TestChatBase

class TestSuspension(TestChatBase):
    def test_suspended_user_message(self):
        """checking if banned users can send message"""
        larry_id = get_user_id("l@rry")
        result = send_message(larry_id, 3, "Can I send this?")
        self.assertFalse(result['sent'])
        self.assertEqual(result['message'], "User is suspended")
        
        # Verify no message in database
        message = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE sender_id = %s AND message_content = 'Can I send this?'
        """, (larry_id,))
        self.assertEqual(message[0], 0)

    def test_paul_suspension_and_messaging(self):
        """testing paul's community timeout"""
        paul_id = get_user_id("Paul")
        arrakis_id = get_community_id("Arrakis")
        comedy_id = get_community_id("Comedy")
        worms_id = get_channel_id("Worms")
        argument_clinic_id = get_channel_id("ArgumentClinic")
        
        # Suspend Paul from Arrakis
        suspend_result = suspend_user_from_community(
            paul_id, arrakis_id, "2024-02-10", "2024-03-10"
        )
        self.assertTrue(suspend_result['sent'])
        
        # Verify suspension in database
        suspension = exec_get_one("""
            SELECT user_id, community_id, start_date, end_date
            FROM suspensions
            WHERE user_id = %s AND community_id = %s
        """, (paul_id, arrakis_id))
        self.assertEqual(suspension[0], paul_id)
        self.assertEqual(suspension[1], arrakis_id)
        
        # Try sending messages
        worms_message = send_channel_message(paul_id, worms_id, "Test message")
        self.assertTrue(worms_message['sent'])
        
        # Join Comedy and send message
        join_community(paul_id, comedy_id)
        comedy_message = send_channel_message(paul_id, argument_clinic_id, "Test message")
        self.assertTrue(comedy_message['sent'])
        
        # Verify in database
        messages = exec_get_one("""
            SELECT COUNT(*) FROM messages 
            WHERE sender_id = %s AND channel_id = %s
        """, (paul_id, argument_clinic_id))
        self.assertEqual(messages[0], 1)