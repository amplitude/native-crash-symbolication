from tornado.options import options
from tornado.options import define

define('crashesdb', default='postgresql://postgres@localhost/crashes', help='Events Database URI')

define('accountdb_host', default='localhost', help='Account Database')
define('accountdb_user', default='account', help='Account Username')
define('accountdb_password', default=None, help='Account Password')
define('accountdb_database', default='account', help='Account Database Name')
