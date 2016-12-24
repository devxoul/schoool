# -*- coding: utf-8 -*-

from redis import StrictRedis


class RedisClient(object):

    _redis = None

    def init_app(self, app):
        self._redis = StrictRedis.from_url(app.config['REDIS_URL'])

    def __getattr__(self, name):
        return getattr(self._redis, name)

    def __setattr__(self, name, val):
        if name == '_redis':
            super(RedisClient, self).__setattr__(name, val)
        else:
            self._redis.__setattr__(name, val)


client = RedisClient()
init_app = client.init_app


def keys(pattern):
    return client.keys(pattern)


def get(key):
    return client.get(key)


def set(key, value):
    return client.set(key, value)


def mget(*keys):
    return client.mget(*keys)


def delete(key):
    return client.delete(key)
