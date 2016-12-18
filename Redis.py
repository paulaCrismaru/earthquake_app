import redis


db = None

class DB():
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushall()

    def is_cached(self):
        pass

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, value, expire=None):
        self.redis.set(key, value, expire)

    def get_list(self, key, start=0, stop=-1):
        return self.redis.lrange(key, start, stop)

    def append_to_list(self, key, *values):
        self.redis.rpush(key, *values)

    def set_expire(self, key, seconds):
        self.redis.expire(key, seconds)
