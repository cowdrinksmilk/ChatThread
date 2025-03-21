import re
from datetime import datetime, date
import csv
from src.swen344_db_utils import exec_get_all, exec_get_one, exec_get_all_dict, exec_commit
from .user import get_user_id, get_user_id_by_id
from .suspension import is_user_suspended, is_user_suspended_in_community

def get_messages_on_specific_date(date_str):
    """finds messages from a certain day"""
    try:
        find_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        result = exec_get_all("SELECT * FROM messages WHERE DATE(timestamp) = %(date)s", {'date': find_date})
        return result if result else f"No messages sent on {date_str}"
    except ValueError:
        return "Date format must be: YYYY-MM-DD."

def send_message(sender_id, receiver_id, content, timestamp=None):
    """sends a dm to someone"""
    if timestamp is None:
        timestamp = datetime.now()
    try:
        # Get sender's username for suspension check
        username = get_user_id_by_id(sender_id)
        if is_user_suspended(username, timestamp.strftime('%Y-%m-%d')):
            return {'sent': False, 'message': 'User is suspended'}
            
        exec_commit("""
            INSERT INTO messages 
            (sender_id, receiver_id, message_content, timestamp, is_read, is_direct_message)
            VALUES (%s, %s, %s, %s, FALSE, TRUE)
        """, (sender_id, receiver_id, content, timestamp))
        return {'sent': True, 'message': 'Message sent'}
    except Exception as e:
        return {'sent': False, 'message': str(e)}


def send_channel_message(sender_id, channel_id, content, timestamp=None):
    """posts a message in a channel"""
    if timestamp is None:
        timestamp = datetime.now()
    try:
        # Get community info
        community_info = exec_get_one("""
            SELECT c.community_id 
            FROM channels ch
            JOIN communities c ON c.community_id = ch.community_id
            WHERE ch.channel_id = %s
        """, (channel_id,))
        
        if not community_info:
            return {'sent': False, 'error': 'Channel not found'}
            
        community_id = community_info[0]
        
        # Check suspension first
        suspension_check = exec_get_one("""
            SELECT end_date 
            FROM suspensions 
            WHERE user_id = %s 
            AND community_id = %s
            AND start_date <= %s 
            AND end_date >= %s
        """, (sender_id, community_id, timestamp, timestamp))
        
        if suspension_check:
            return {
                'sent': False, 
                'error': f'User suspended until {suspension_check[0]}'
            }
            
        # Then check membership
        member_check = exec_get_one("""
            SELECT 1 FROM community_members 
            WHERE user_id = %s AND community_id = %s
        """, (sender_id, community_id))
        
        if not member_check:
            return {'sent': False, 'error': 'Not a member'}
            
        # If checks pass, send message
        message_id = exec_get_one("""
            INSERT INTO messages 
            (sender_id, channel_id, message_content, timestamp, is_direct_message)
            VALUES (%s, %s, %s, %s, FALSE)
            RETURNING message_id
        """, (sender_id, channel_id, content, timestamp))[0]
        
        mentions_content(content, message_id, community_id)
        return {'sent': True}
        
    except Exception as e:
        return {'sent': False, 'error': str(e)}
    
def mentions_content(content, message_id, community_id):
    """handles @ mentions in messages"""
    try:
        mentions = re.findall(r'@(\w+)', content)
        if not mentions:
            return
            
        for username in mentions:
            exec_commit("""
                INSERT INTO mentions (message_id, mentioned_user_id)
                SELECT m.message_id, u.user_id
                FROM messages m
                JOIN users u ON u.username = %s
                JOIN community_members cm ON cm.user_id = u.user_id
                WHERE m.message_id = %s
                AND cm.community_id = %s
            """, (username, message_id, community_id))
    except Exception:
        pass

def get_messages_between_users(u1_id, u2_id, start_date=None, end_date=None):
    """gets all messages between two people"""
    sql = """
        SELECT * FROM messages
        WHERE ((sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s))
            AND is_direct_message = TRUE
        {date_filter}
        ORDER BY timestamp;
    """.format(date_filter="" if not start_date or not end_date else "AND timestamp BETWEEN %s AND %s")
    
    args = [u1_id, u2_id, u2_id, u1_id]
    if start_date and end_date:
        try:
            start_find_date = (datetime.combine(start_date, datetime.min.time()) 
                            if isinstance(start_date, date) 
                            else datetime.strptime(start_date, '%Y-%m-%d'))
            end_find_date = (datetime.combine(end_date, datetime.max.time())
                          if isinstance(end_date, date)
                          else datetime.strptime(end_date, '%Y-%m-%d'))
            args.extend([start_find_date, end_find_date])
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
    return exec_get_all_dict(sql, args)

def get_message_senders(user_id):
    """shows who's been messaging you"""
    sql = """
        SELECT 
            u.user_id,
            u.username,
            COUNT(CASE WHEN m.is_read = FALSE THEN 1 END) as unread_count,
            MAX(m.timestamp) as last_message
        FROM users u
        JOIN messages m ON m.sender_id = u.user_id
        WHERE m.receiver_id = %s AND m.is_direct_message = TRUE
        GROUP BY u.user_id, u.username
        ORDER BY last_message DESC
    """
    return exec_get_all_dict(sql, (user_id,))

def get_user_mentions(user_id):
    """finds where someone @ mentioned you"""
    sql = """
        SELECT m.*, u.username as sender_username
        FROM messages m
        JOIN mentions mt ON mt.message_id = m.message_id
        JOIN users u ON u.user_id = m.sender_id
        WHERE mt.mentioned_user_id = %s
        ORDER BY m.timestamp DESC
    """
    return exec_get_all_dict(sql, (user_id,))

def import_chat_data(file_path='tests/whos_on_first.csv'):
    """loads chat history from a file"""
    abbott_id = get_user_id("ab0tt")
    costello_id = get_user_id("costell0")
    count = 0
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            
            for row in reader:
                if len(row) >= 2:
                    sender = row[0].strip()
                    message = row[1].strip()
                    
                    if not sender or not message:
                        continue
                        
                    sender_id = abbott_id if sender == "Abbott" else costello_id
                    receiver_id = costello_id if sender == "Abbott" else abbott_id
                    
                    exec_commit("""
                        INSERT INTO messages 
                        (sender_id, receiver_id, message_content, is_read, is_direct_message)
                        VALUES (%s, %s, %s, FALSE, TRUE)
                    """, (sender_id, receiver_id, message))
                    count += 1
                    
        return {'sent': True, 'messages_imported': count}
    except Exception as e:
        return {'sent': False, 'error': str(e)}