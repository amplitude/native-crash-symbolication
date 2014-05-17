import amp.db.settings
from tornado.options import define
from amp.util import configloader

define('port', default=3000, help='The port the server listens on')
define('debug', default=False, help='If True, runs the server in debug mode')
define('base_url', default='/', help='The base url for all pages')

define('ssl_cert', default=None, help='The path to the ssl certificate')
define('ssl_key', default=None, help='The path to the ssl key')

define('cookie_secret', default='00000000000000000000000000000000000000000000')
define('template_path', default='templates', help='Lookup path for templates')
define('static_path', default='public', help='Path to static files')


def load(ignore_command_line=False):
    configloader.load()


if __name__ == '__main__':
    configloader.out()
