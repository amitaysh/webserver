import elasticache_auto_discovery
from pymemcache.client.hash import HashClient
import redis
import boto3
import config


class MemCacheHandler:
    def __init__(self):
        nodes = elasticache_auto_discovery.discover(config.cacheHandler['memchached_endpoint'])
        nodes = map(lambda x: (x[1], int(x[2])), nodes)
        self.cache_client = HashClient(nodes)

    def push(self, key, val):
        self.cache_client.set(key, val)

    def pull(self, key):
        return self.cache_client.get(key)

    def delete(self, key):
        self.cache_client.delete(key)


class RedisHandler:
    def __init__(self):
        self.cache_client = redis.Redis(host=config.cacheHandler['redis_endpoint'], port=6379, db=0)

    def push(self, key, val):
        self.cache_client.set(key, val)

    def pull(self, key):
        return self.cache_client.get(key)

    def delete(self, key):
        self.cache_client.delete(key)


class Boto3Handler:
    def __init__(self):
        session = boto3.Session(aws_access_key_id=config.cacheHandler['key'], aws_secret_access_key=config.cacheHandler['secret'])
        self.cache_client = session.client('ecr', region_name='us-west-2')
        self.repository_endpoint = config.cacheHandler['repository_endpoint']

    def push(self, key, val):
        self.cache_client.tag_resource(
            resourceArn=self.repository_endpoint,
            tags=[
                {
                    'Key': key,
                    'Value': str(val)
                },
            ]
        )

    def pull(self, key):
        tags = self.cache_client.list_tags_for_resource(
            resourceArn=self.repository_endpoint
        )
        for tag in tags['tags']:
            if 'Key' in tag and tag['Key'] == key:
                return tag['Value']
        return '0'

    def delete(self, key):
        self.cache_client.untag_resource(
            resourceArn=self.repository_endpoint,
            tagKeys=[key]
        )
