import torndb
from amp.db.settings import options

conn = None


def new():
    return torndb.Connection(
        options.accountdb_host,
        options.accountdb_database,
        options.accountdb_user,
        options.accountdb_password)

def connect():
    global conn
    if conn is None:
        conn = new()
    return conn
