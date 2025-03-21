# queries for analyzing stuff
from src.swen344_db_utils import exec_get_all_dict, exec_get_one

def search_messages(search_text, community_id=None):
    # basic message search
    q = """
        select distinct m.message_id, m.message_content, 
            m.timestamp, u.username as sender
        from messages m
        join users u on m.sender_id = u.user_id 
        where to_tsvector('english', m.message_content) @@ 
            plainto_tsquery('english', %s)
    """
    
    params = [search_text]
    
    # add community filter
    if community_id:
        q += """
            and exists (select 1 from channels ch 
            where ch.channel_id = m.channel_id 
            and ch.community_id = %s)"""
        params.append(community_id)
        
    q += " order by m.timestamp desc"
    return exec_get_all_dict(q, tuple(params))

def get_activity_summary(ref_date):
    # get stats about messages and users
    q = """
        with time_window as (
            select %s::date as end_date,
                   %s::date - interval '30 days' as start_date
        ),
        activity as (
            select c.name as community,
                   count(distinct case when length(m.message_content) > 5 
                   and m.timestamp between w.start_date and w.end_date 
                   then m.message_id end)::float / 30.0 as messages_per_day,
                   count(distinct case when length(m.message_content) > 5
                   and m.timestamp between w.start_date and w.end_date
                   then m.sender_id end) as active_users
            from communities c
            cross join time_window w
                left join channels ch on ch.community_id = c.community_id  
                left join messages m on m.channel_id = ch.channel_id
            group by c.name
        )


        select community,
               round((coalesce(messages_per_day, 0.0))::numeric, 1) as avg_num_messages,
               coalesce(active_users, 0) as active_users
        from activity
        order by messages_per_day desc"""
    
    return exec_get_all_dict(q, (ref_date, ref_date))

def get_suspended_active_users(start_date, end_date):
    # find people who are suspended but sent messages
    q = """select distinct u.username,
           c.name as suspended_from,
           s.start_date, s.end_date,
           s.suspension_reason
        from users u
            join messages m on m.sender_id = u.user_id
            join suspensions s on s.user_id = u.user_id
            join communities c on c.community_id = s.community_id
        where m.timestamp between %s::date and %s::date
        and s.end_date > current_timestamp
        and s.start_date <= current_timestamp
        order by u.username, c.name"""
    
    return exec_get_all_dict(q, (start_date, end_date))