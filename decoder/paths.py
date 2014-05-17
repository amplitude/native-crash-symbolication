import base64
import os


def filename_escape(name):
    if type(name) == unicode:
        name = name.encode('utf8')
    return base64.urlsafe_b64encode(name).rstrip("=")


def filename_decode(name):
    # add back equal sign padding, return as unicode string
    return base64.urlsafe_b64decode(name + "=" * (-len(name) % 4)).decode('utf-8')


def minidump_path(app_db, crash):
    return os.path.join(app_db, 'minidumps', crash)


def lib_tar_path(app_db, version):
    return os.path.join(app_db, 'libs', filename_escape(version) + '.tar.gz')


def lib_extract_dir_path(app_db, version):
    return os.path.join(app_db, 'libs', filename_escape(version))


def trace_dir_path(app_db):
    return os.path.join(app_db, 'traces')


def trace_out_path(app_db, crash):
    return os.path.join(trace_dir_path(app_db), crash + '.amp.txt')


def trace_err_path(app_db, crash):
    return os.path.join(trace_dir_path(app_db), crash + '.amp.err')
