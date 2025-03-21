from src.swen344_db_utils import exec_commit, exec_get_one
from src.chat.models.user import (
    get_all_users, check_user_exists_by_username, check_user_exists_by_id,
    get_user_id, change_username
)
from .test_base import TestChatBase

class TestUsers(TestChatBase):
    def test_get_all_users(self):
        """make sure we got enough users"""
        result = get_all_users()
        self.assertGreaterEqual(len(result), 7)

    def test_user_exists(self):
        """just checking if user is there"""
        result = check_user_exists_by_id(1)
        self.assertGreater(len(result), 0)

    def test_user_does_not_exist(self):
        """making sure fake users don't exist"""
        result = check_user_exists_by_username("nonexistent")
        self.assertFalse(result)

    def test_paul_exists(self):
        """is paul around"""
        result = check_user_exists_by_username("Paul")
        self.assertTrue(result)
        
        # Validate Paul's basic info
        paul_info = exec_get_one(
            "SELECT username, email FROM users WHERE username = 'Paul'"
        )
        self.assertEqual(paul_info[0], "Paul")
        self.assertEqual(paul_info[1], "paul@dune.com")

    def test_username_change_restriction(self):
        """can't change names too often"""
        bob_id = get_user_id("Bob")
        
        # Try changing name
        result = change_username(bob_id, "BabySteps2Elevator", "1991-05-20")
        self.assertIn("more days", result)
        
        # Verify username didn't change
        current_name = exec_get_one(
            "SELECT username FROM users WHERE user_id = %s",
            (bob_id,)
        )
        self.assertEqual(current_name[0], "Bob")

    def test_username_change(self):
        """changing bob's name"""
        bob_id = get_user_id("Bob")
        exec_commit(
            "UPDATE users SET last_username_change = '2024-01-01' WHERE user_id = %s",
            (bob_id,)
        )
        result = change_username(bob_id, "BabySteps2Door", "2025-02-04")
        self.assertEqual(result, "Username changed.")
        
        # Verify change in database
        new_name = exec_get_one(
            "SELECT username FROM users WHERE user_id = %s",
            (bob_id,)
        )
        self.assertEqual(new_name[0], "BabySteps2Door")

    def test_username_change_days_remaining(self):
        """checking the name change timer"""
        bob_id = get_user_id("Bob")
        exec_commit(
            "UPDATE users SET last_username_change = '2025-01-01' WHERE user_id = %s",
            (bob_id,)
        )
        result = change_username(bob_id, "NewName", "2025-02-01")
        self.assertIn("149 more days", result)