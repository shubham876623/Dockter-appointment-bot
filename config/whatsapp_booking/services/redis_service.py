import redis

class RedisService:
    client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    @classmethod
    def set_session(cls, user_key, data):
        cls.client.hmset(user_key, data)

    @classmethod
    def get_session(cls, user_key):
        return cls.client.hgetall(user_key)

    @classmethod
    def clear_session(cls, user_key):
        cls.client.delete(user_key)
