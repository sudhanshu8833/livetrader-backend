# standard imports
import logging
import redis
import json

from django.conf import settings
from contextlib import contextmanager

@contextmanager
def redis_lock(lock_key, timeout = None):
    redis_client = settings.REDIS_CLIENT
    lock = redis_client.setnx(lock_key, 'locked')
    if lock:
        if timeout!=None:
            redis_client.expire(lock_key, timeout)
        try:
            yield
        except Exception as e:
            print(f'Error in redis lock: {str(e)}')
        finally:
            redis_client.delete(lock_key)
    else:
        print('Price feed already running')

# django imports
from rest_framework.response import Response

# local imports

logging.getLogger("urllib3").setLevel(logging.WARNING)
error = logging.getLogger('error_log')
dev = logging.getLogger('dev_log')

def log_info(message):
    dev.info(message)

def log_error(message):
    error.error(message)