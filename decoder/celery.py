from __future__ import absolute_import

from celery import Celery

celery = Celery('decoder.celery',
                include=['decoder.tasks'])

celery.config_from_object('decoder.config:')
celery.config_from_object('decoder.localconfig:', silent=True)

if __name__ == '__main__':
    celery.start()
