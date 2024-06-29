import os
import redis
from rq import Worker, Queue, Connection


listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', "redis://:p48e3f76d46bfa822a740e698d14b517e49d2952955d8227d6c89dcebf2d6b092@ec2-35-171-140-156.compute-1.amazonaws.com:30879")

conn = redis.from_url(redis_url)


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
