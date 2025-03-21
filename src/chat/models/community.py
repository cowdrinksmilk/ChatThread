from src.swen344_db_utils import exec_get_one, exec_commit

def get_community_id(name):
    """finds a community by name"""
    result = exec_get_one("SELECT community_id FROM communities WHERE name = %s", (name,))
    return result[0] if result else None

def join_community(user_id, community_id):
    """adds someone to a community"""
    try:
        exec_commit("""
            INSERT INTO community_members (user_id, community_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """, (user_id, community_id))
        return {'sent': True}
    except Exception as e:
        return {'sent': False, 'error': str(e)}

def leave_community(user_id, community_id):
    """kicks someone out of a community"""
    try:
        exec_commit("""
            DELETE FROM community_members
            WHERE user_id = %s AND community_id = %s
            """, (user_id, community_id))
        return {'sent': True}
    except Exception as e:
        return {'sent': False, 'error': str(e)}

def check_community_membership(user_id, community_id):
    """checks if someone's in a community"""
    result = exec_get_one("""
        SELECT COUNT(*) FROM community_members
        WHERE user_id = %s AND community_id = %s
        """, (user_id, community_id))
    return result[0] > 0 if result else False

def get_channel_id(name):
    """looks up a channel by name"""
    result = exec_get_one("SELECT channel_id FROM channels WHERE name = %s", (name,))
    return result[0] if result else None