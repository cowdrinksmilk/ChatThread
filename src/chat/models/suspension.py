from datetime import datetime
from src.swen344_db_utils import exec_get_one, exec_commit
from .user import get_user_id

def is_user_suspended(username, check_date):
    """checks if someone's banned"""
    user_id = get_user_id(username)
    if not user_id:
        return False
    sql = """
        SELECT COUNT(*) FROM suspensions
        WHERE user_id = %s AND start_date <= %s AND end_date >= %s
        """
    check_find_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    result = exec_get_one(sql, (user_id, check_find_date, check_find_date))
    return result[0] > 0 if result else False

def is_user_suspended_in_community(user_id, community_id, check_date=None):
    """sees if someone's banned from a community"""
    if check_date is None:
        check_date = datetime.now()
    if isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d')
    sql = """
        SELECT COUNT(*) FROM suspensions
        WHERE user_id = %s
        AND community_id = %s
        AND start_date <= %s
        AND end_date >= %s
        """
    result = exec_get_one(sql, (user_id, community_id, check_date, check_date))
    return result[0] > 0 if result else False

def suspend_user_from_community(user_id, community_id, start_date, end_date):
    """kicks someone out of a community temporarily"""
    try:
        starting_date = datetime.strptime(start_date, '%Y-%m-%d')
        ending_date = datetime.strptime(end_date, '%Y-%m-%d')
        exec_commit("""
            INSERT INTO suspensions
            (user_id, community_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            """, (user_id, community_id, starting_date, ending_date))
        return {'sent': True}
    except Exception as e:
        return {'sent': False, 'error': str(e)}

def unsuspend_user_from_community(user_id, community_id):
    """lets someone back into a community"""
    try:
        exec_commit("""
            DELETE FROM suspensions
            WHERE user_id = %s
            AND community_id = %s
            AND end_date > CURRENT_TIMESTAMP
            """, (user_id, community_id))
        return {'sent': True}
    except Exception as e:
        return {'sent': False, 'error': str(e)}