from src.swen344_db_utils import *

def rebuildTables():
    """resets the database to a clean state"""
    exec_sql_file('src/chatschema.sql')
    exec_sql_file('tests/test_chatschema.sql')

def check_database_seed():
    """makes sure we got data in all our tables"""
    tables = [
        exec_get_all("SELECT * FROM users"),
        exec_get_all("SELECT * FROM messages"),
        exec_get_all("SELECT * FROM suspensions"),
        exec_get_all("SELECT * FROM communities"),
        exec_get_all("SELECT * FROM channels"),
        exec_get_all("SELECT * FROM community_members")
    ]
    return tables