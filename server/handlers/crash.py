import datetime
import json
from tornado.web import RequestHandler, HTTPError
from sqlalchemy.sql import select, text, bindparam
from sqlalchemy import MetaData
from decoder.tasks import breakpad_decode, save_lib, save_minidump
from amp.db.crashes import engine as crashes_db
from amp.db.crashes import crashes
from amp.util.date import millisfromepoch
from server.handlers import account
from server.handlers import BaseHandler, require_basic_auth

class UploadCrashHandler(BaseHandler):

    def post(self):
        api_key = self.get_argument('apiKey')
        app_db = account.get_db_for_api_key(api_key)
        if app_db is None:
            raise HTTPError(400, 'Invalid API Key')
#        app = self.get_argument('appName')
        version = self.get_argument('version')
        try:
            version_code = int(self.get_argument('versionCode', -1))
        except ValueError as e:
            version_code = -1


        now = datetime.datetime.utcnow()
        try:
            crashtime = datetime.datetime.utcfromtimestamp(int(self.get_argument('crashtime', None)) / 1000.0)
        except (ValueError, TypeError):
            crashtime = now

        try:
            uploadtime = datetime.datetime.utcfromtimestamp(int(self.get_argument('uploadtime', None)) / 1000.0)
        except (ValueError, TypeError):
            uploadtime = now

        try:
            extras_string = self.get_argument('extras', '{}')
            extras = json.loads(extras_string)
        except (ValueError, TypeError):
            extras_string = '{}'
            extras = {}

        # adjust crash time
        crashtime = now - (uploadtime - crashtime)


        f = self.request.files.get('minidump', None)
        if f is None or len(f) == 0:
            raise HTTPError(400, 'No file found')
        filename = f[0]['filename']

        save_minidump(app_db, filename, f[0]['body'])

        conn = crashes_db.connect()
        conn.execute("SET search_path TO %s", (app_db,))
        conn.execute(crashes.insert(), version=version, version_code=version_code, crash=filename, crashtime=crashtime, extras=extras_string, uploadtime=now)
        conn.execute("SET search_path TO 'public'")
        conn.close()

        breakpad_decode.delay(filename, app_db, version)
        self.write(filename)
        return


class RestReprocessCrashHandler(RequestHandler):

    def post(self):
        api_key = self.get_argument('api_key')
        crash_id = self.get_argument('crash')
        app_db = account.get_db_for_api_key(api_key)
        if app_db is None:
            raise HTTPError(403, 'Invalid API Key')

        conn = crashes_db.connect()
        conn.execute("SET search_path TO %s", (app_db,))
        result = conn.execute(select([crashes.c.version, crashes.c.version_code],
                                 crashes.c.crash == crash_id))
        row = result.fetchone()
        conn.execute("SET search_path TO 'public'")
        conn.close()
        if row is None:
            raise HTTPError(404)
        version = row[0]
        breakpad_decode.delay(crash_id, app_db, version)
        self.write('0')
        return


class RestUploadLibHandler(BaseHandler):

    def post(self, build_version=''):
        api_key = self.get_argument('api_key')
        build_version = self.get_argument('version', build_version)
        app_db = account.get_db_for_api_key(api_key)
        if app_db == None:
            raise HTTPError(403, 'Invalid API Key')
        result = save_lib(app_db, self.request.body, build_version)
        self.write(str(result))
        return

    def put(self, build_version=''):
        return self.post(build_version)

@require_basic_auth
class RestExportCrashesHandler(RequestHandler):
    
    SIGNAL_TO_INT = {
        'SIG_DFL': 0,
        'SIGHUP': 1,
        'SIG_IGN': 1,
        'SIGINT': 2,
        'SIGQUIT': 3,
        'SIGILL': 4,
        'SIGTRAP': 5,
        'SIGABRT': 6,
        'SIGIOT': 6,
        'SIGBUS': 7,
        'SIGFPE': 8,
        'SIGKILL': 9,
        'SIGUSR1': 10,
        'SIGSEGV': 11,
        'SIGUSR2': 12,
        'SIGPIPE': 13,
        'SIGALRM': 14,
        'SIGTERM': 15,
        'SIGSTKFLT': 16,
        'SIGCLD': 17,
        'SIGCHLD': 17,
        'SIGCONT': 18,
        'SIGSTOP': 19,
        'SIGTSTP': 20,
        'SIGTTIN': 21,
        'SIGTTOU': 22,
        'SIGURG': 23,
        'SIGXCPU': 24,
        'SIGXFSZ': 25,
        'SIGVTALRM': 26,
        'SIGPROF': 27,
        'SIGWINCH': 28,
        'SIGIO': 29,
        'SIGPOLL': 29,
        'SIGPWR': 30,
        'SIGSYS': 31,
        'SIGUNUSED': 31
    }
    
    def convert_signal(self, signal):
        return self.SIGNAL_TO_INT.get(signal, None)
    
    def convert_crash(self, app, crashid, crash, crashtime, uploadtime, version, version_code, crash_reason, crash_address, crash_line, extras, stacktrace):
        try:
            extras = json.loads(extras)
        except:
            extras = {}
        converted = {
            '_id': crashid,
            'crash': crash,
            'crashtime': millisfromepoch(crashtime),
            'uploadtime': millisfromepoch(uploadtime),
            'version': version,
            'version_code': version_code,
            'crash_signal': crash_reason,
            'crash_signal_value': self.convert_signal(crash_reason),
            'crash_address': crash_address,
            'crash_line': crash_line,
            'app_name': extras.get('app_name', None),
            'carrier': extras.get('carrier', None),
            'device_manufacturer': extras.get('device_manufacturer', None),
            'device_brand': extras.get('device_brand', None),
            'device_model': extras.get('device_model', None),
            'platform': extras.get('platform', None),
            'platform_sdk': extras.get('platform_sdk', None),
            'platform_release': extras.get('platform_release', None),
            'country': extras.get('country', None),
            'language': extras.get('language', None),
            'extras': extras.get('extras', None),
            'stacktrace': stacktrace,
            'view_url': 'https://amplitude.com/app/%s/crashes?c=%s' % (app, crash)
        }
        return converted

    def get(self, basicauth_user, basicauth_pass):
        app_db = account.get_db_for_api_key(basicauth_user)
        if app_db is None:
            raise HTTPError(403, 'Invalid API Key')
        app = account.get_app_for_api_key(basicauth_user)
        app_id = app.get('app_id', None)
        secret_key = app.get('secret_key', None)
        if secret_key is None or secret_key != basicauth_pass:
            raise HTTPError(403, 'Invalid API/Secret Key combination')
        
        try:
            after = int(self.get_argument('after')) / 1000.0
        except ValueError:
            raise HTTPError(400, 'Invalid argument after')
        try:
            limit = int(self.get_argument('n', 1000))
        except:
            limit = 1000

        with crashes_db.connect() as conn:
            metadata = MetaData()
            table = crashes.tometadata(metadata, schema=app_db)
            result = conn.execute(select([
                table.c.id,
                table.c.crash,
                table.c.crashtime,
                table.c.uploadtime,
                table.c.version,
                table.c.version_code,
                table.c.crash_reason,
                table.c.crash_address,
                table.c.crash_line,
                table.c.extras,
                table.c.crashed_thread_stacktrace
                ]).where(table.c.uploadtime>=text('to_timestamp(:after)', bindparams=[bindparam('after', after)])).order_by(table.c.uploadtime).limit(limit))
            fetched_crashes = []
            for row in result:
                fetched_crashes.append(self.convert_crash(
                    app_id,
                    row[table.c.id],
                    row[table.c.crash],
                    row[table.c.crashtime],
                    row[table.c.uploadtime],
                    row[table.c.version],
                    row[table.c.version_code],
                    row[table.c.crash_reason],
                    row[table.c.crash_address],
                    row[table.c.crash_line],
                    row[table.c.extras],
                    row[table.c.crashed_thread_stacktrace]
                    ))
            self.write(json.dumps(fetched_crashes))
