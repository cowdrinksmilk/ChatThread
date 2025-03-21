from src.swen344_db_utils import exec_get_all_dict, exec_get_one, exec_commit

def mark_messages_as_read(user_id, sender_id):
    """marks all dms from someone as read"""
    try:
        exec_commit("""
            UPDATE messages
            SET is_read = TRUE
            WHERE receiver_id = %s AND sender_id = %s AND is_direct_message = TRUE
            """, (user_id, sender_id))
        return {'sent': True}
    except Exception as e:
        return {'sent': False, 'error': str(e)}

def count_unread_messages(user_id):
    """counts how many unread dms you have"""
    sql = """
        SELECT COUNT(*) FROM messages
        WHERE receiver_id = %s AND is_read = FALSE AND is_direct_message = TRUE;
        """
    result = exec_get_one(sql, (user_id,))
    return result[0] if result else 0

def count_direct_messages(u1_id, u2_id):
    """counts total dms between two people"""
    sql = """
        SELECT COUNT(*) FROM messages
        WHERE ((sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s))
            AND is_direct_message = TRUE
        """
    result = exec_get_one(sql, (u1_id, u2_id, u2_id, u1_id))
    return result[0] if result else 0

def get_unread_counts_by_sender(user_id):
    """checks who's sent you unread stuff"""
    sql = """
        SELECT u.username, COUNT(*) as unread_count
        FROM messages m
        JOIN users u ON m.sender_id = u.user_id
        WHERE m.receiver_id = %s AND m.is_read = FALSE AND m.is_direct_message = TRUE
        GROUP BY u.user_id, u.username
        """
    return exec_get_all_dict(sql, (user_id,))

def get_user_unread_counts(user_id):
    """gets all your unread counts everywhere"""
    community_sql = """
        SELECT c.name, COUNT(m.*) as unread_count
        FROM communities c
        JOIN channels ch ON ch.community_id = c.community_id
        JOIN messages m ON m.channel_id = ch.channel_id
        JOIN community_members cm ON cm.community_id = c.community_id
        WHERE cm.user_id = %s AND m.is_read = FALSE
        GROUP BY c.name
        """
    channel_sql = """
        SELECT ch.name, COUNT(m.*) as unread_count
        FROM channels ch
        JOIN messages m ON m.channel_id = ch.channel_id
        JOIN community_members cm ON cm.community_id = ch.community_id
        WHERE cm.user_id = %s AND m.is_read = FALSE
        GROUP BY ch.name
        """
    dm_sql = """
        SELECT COUNT(*) as unread_count
        FROM messages
        WHERE receiver_id = %s
        AND is_direct_message = TRUE
        AND is_read = FALSE
        """
    community_unread = {row['name']: row['unread_count']
                      for row in exec_get_all_dict(community_sql, (user_id,))}
    channel_unread = {row['name']: row['unread_count']
                     for row in exec_get_all_dict(channel_sql, (user_id,))}
    dm_unread = exec_get_one(dm_sql, (user_id,))[0]
    return {
        'community_unread': community_unread,
        'channel_unread': channel_unread,
        'dm_unread': dm_unread
    }