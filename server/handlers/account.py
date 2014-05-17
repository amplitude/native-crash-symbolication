import logging

from amp.db.account.connection import connect
from amp.db.account.errors import MySQLError


_logger = logging.getLogger(__name__)

def get_db_for_app_url(login_id, app_url):
    db = connect()
    try:
        row = db.get('SELECT app_db FROM apps WHERE app_id=%s', app_url)
        if row:
            return row.app_db
        return None
    except MySQLError as e:
        raise e

def get_db_for_api_key(api_key):
    db = connect()
    row = db.get("SELECT app_db FROM apps WHERE api_key=%s", api_key)
    if row:
        return row.app_db
    return None

def get_app_for_api_key(api_key):
    db = connect()
    row = db.get("select app_id, secret_key from apps where api_key=%s", api_key)
    if row:
        return {'app_id': row.app_id,
                'secret_key': row.secret_key}
    return None
