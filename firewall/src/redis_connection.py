import redis
from configs import redis_config


def get_redis_connection():
    return redis.StrictRedis(host=redis_config['host'],
                             port=redis_config['port'],
                             db=redis_config['db'],
                             socket_keepalive=True,
                             socket_connect_timeout=10,
                             socket_timeout=10000000,
                             decode_responses=False)
