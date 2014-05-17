from __future__ import absolute_import

import os
import re
import subprocess

from amp.util.osutils import makedirs
from amp.aws.s3cache import S3Cache

from amp.db.crashes import engine
from amp.db.crashes import crashes

from decoder import paths
from decoder.celery import celery

from sqlalchemy.sql import select, and_


BASE_DIR = celery.conf.get('BASE_DIR')

MINIDUMP_STACKWALK_EXEC = BASE_DIR + 'minidump_stackwalk'
EXTRACT_SYMS_EXEC = BASE_DIR + 'extract_syms'

AWS_ACCESS_KEY_ID = celery.conf.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = celery.conf.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET = celery.conf.get('AWS_BUCKET')
AWS_CACHE_DIR = celery.conf.get('AWS_CACHE_DIR')

s3 = S3Cache(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET, AWS_CACHE_DIR)




def save_minidump(app_db, crash, content):
    s3.put(paths.minidump_path(app_db, crash), content)


def save_lib(app_db, content, version):
    lib_path = paths.lib_tar_path(app_db, version)
    extract_path = paths.lib_extract_dir_path(app_db, version)
    # upload to s3
    s3.put(lib_path, content)
    # extract syms
    breakpad_extract_syms.delay(s3.localpath(lib_path), s3.localpath(extract_path))
    return 0


@celery.task
def breakpad_decode(crash, app_db, version):
    trace_dir = paths.trace_dir_path(app_db)
    outfilepath = paths.trace_out_path(app_db, crash)
    errfilepath = paths.trace_err_path(app_db, crash)

    # make sure trace_dir exists
    makedirs(s3.localpath(trace_dir), exist_ok=True)

    minidump_path = paths.minidump_path(app_db, crash)
    lib_path = paths.lib_extract_dir_path(app_db, version)
    symbols_path = os.path.join(lib_path, 'symbols')
    lib_tar_path = paths.lib_tar_path(app_db, version)

    s3.get(minidump_path)
    if not os.path.exists(s3.localpath(symbols_path)):
        # pull from s3 and untar
        s3.get(lib_tar_path)
        breakpad_extract_syms(s3.localpath(lib_tar_path),
                              s3.localpath(lib_path))

    p = 1
    with open(s3.localpath(outfilepath), 'wb') as outfile:
        with open(s3.localpath(errfilepath), 'wb') as errfile:
            p = subprocess.call([
                    MINIDUMP_STACKWALK_EXEC,
                    s3.localpath(minidump_path),
                    s3.localpath(symbols_path),
                    ], stdout=outfile, stderr=errfile)

    s3.put_file(outfilepath)
    return p or parse_trace(s3.localpath(outfilepath), crash, app_db)


def parse_trace(minidump_filepath, crash, app_id):
    with open(minidump_filepath, 'rb') as trace:
        crashed = False
        crashed_trace = []
        crash_reason = None
        crash_address = None
        for line in trace:
            if crashed:
                if line == '\n' or line.startswith('Thread'):
                    break
                else:
                    crashed_trace.append(line)
            if '(crashed)' in line:
                crashed = True
            elif line.startswith('Crash reason:  '):
                crash_reason = line[15:].rstrip()
            elif line.startswith('Crash address: '):
                crash_address = line[15:].rstrip()
        if len(crashed_trace) == 0:
            return 0
        else:
            conn = engine.connect()
            conn.execute("SET search_path TO %s", (app_id,))
            crash_line = re.sub(r'^[0-9 ]*[0-9][ ]+', '', crashed_trace[0].rstrip())
            conn.execute(crashes.update().where(crashes.c.crash==crash).values(
                    crash_line=crash_line,
                    crashed_thread_stacktrace=''.join(crashed_trace).rstrip(),
                    crash_reason=crash_reason,
                    crash_address=crash_address))
            conn.execute("SET search_path TO 'public'")
            conn.close()
            return 0


@celery.task
def breakpad_extract_syms(lib_path, extract_path):
    env = os.environ.copy()
    env["PATH"] = BASE_DIR + ":" + env.get("PATH", "")
    p = subprocess.call([
            EXTRACT_SYMS_EXEC,
            lib_path,
            extract_path
            ], env=env)
    return p
