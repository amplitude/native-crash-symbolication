import amp.db.settings
from amp.util import configloader
configloader.load()

from decoder.celery import celery

if __name__ == '__main__':
    celery.start()
