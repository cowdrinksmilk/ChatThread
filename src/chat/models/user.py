from datetime import datetime
from src.swen344_db_utils import exec_get_all, exec_get_one, exec_get_all_dict, exec_commit

def get_all_users():
    """grabs everyone's info"""
    return exec_get_all_dict("SELECT * FROM users")

def check_user_exists_by_username(username):
    """sees if we can find someone by their username"""
    return exec_get_all("SELECT * FROM users WHERE username = %(username)s", {'username': username})

def check_user_exists_by_id(user_id):
    """looks up someone using their id"""
    return exec_get_all("SELECT * FROM users WHERE user_id = %(user_id)s", {'user_id': user_id})

def get_user_id(username):
    """gets someone's id from their username"""
    result = exec_get_one("SELECT user_id FROM users WHERE username = %(username)s", {'username': username})
    return result[0] if result else None

def get_user_id_by_id(user_id):
    """finds a username from their id"""
    result = exec_get_one("SELECT username FROM users WHERE user_id = %s", (user_id,))
    return result[0] if result else None

def change_username(user_id, new_username, change_date):
    """update someone's username"""
    try:
        last_changed = exec_get_one(
            "SELECT last_username_change::date FROM users WHERE user_id = %s",
            (user_id,)
        )[0]
        date = datetime.strptime(change_date, '%Y-%m-%d').date()
        days_from_last_changed = (date - last_changed).days
        if days_from_last_changed < 180:
            days_remaining = 180 - days_from_last_changed
            return f"You must wait {days_remaining} more days"
        exec_commit(
            "UPDATE users SET username = %s, last_username_change = %s WHERE user_id = %s",
            (new_username, date, user_id)
        )
        return "Username changed."
    except Exception as e:
        return str(e)