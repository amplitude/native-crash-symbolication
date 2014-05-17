import os
import logging

from amp.util.osutils import makedirs

from boto.s3.connection import S3Connection
from boto.s3.key import Key

_logger = logging.getLogger(__name__)

class S3Cache(object):
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket, cache_dir):
        self.bucket = bucket
        self.cache_dir = cache_dir
        self.s3 = S3Connection(aws_access_key_id, aws_secret_access_key)
        self.s3bucket = self.s3.get_bucket(self.bucket)

    def s3get(self, key):
        s3key = self.s3bucket.get_key(key)
        if s3key is None:
            return
        filepath = self.localpath(key)
        makedirs(os.path.dirname(filepath), exist_ok=True)
        _logger.debug("Getting %s from S3" % (key,))
        s3key.get_contents_to_filename(filepath)

    def get(self, key):
        filepath = self.localpath(key)
        try:
            with open(filepath, 'rb') as f:
                pass
        except:
            self.s3get(key)

    def localpath(self, key):
        return os.path.join(self.cache_dir, key)

    def open(self, key, *args, **kwargs):
        filepath = self.localpath(key)
        self.get(key)
        return open(filepath, *args, **kwargs)

    def s3put(self, key, content):
        s3key = Key(self.s3bucket, key)
        s3key.set_contents_from_string(content)

    def put(self, key, content):
        self.s3put(key, content)
        filepath = self.localpath(key)
        makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb+') as f:
            f.write(content)

    def put_file(self, key):
        s3key = Key(self.s3bucket, key)
        s3key.set_contents_from_filename(self.localpath(key))
