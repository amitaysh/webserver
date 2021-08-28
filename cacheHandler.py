import elasticache_auto_discovery
from pymemcache.client.hash import HashClient
import redis
import boto3


class MemCacheHandler:
    def __init__(self):
        elasticache_config_endpoint = "memcache.j7lwwv.cfg.usw2.cache.amazonaws.com:11211"
        nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
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
        self.cache_client = redis.Redis(host='cache-cluster.j7lwwv.0001.usw2.cache.amazonaws.com', port=6379, db=1)

    def push(self, key, val):
        self.cache_client.set(key, val)

    def pull(self, key):
        return self.cache_client.get(key)

    def delete(self, key):
        self.cache_client.delete(key)


class Boto3Handler:
    def __init__(self):
        session = boto3.Session(aws_access_key_id='************', aws_secret_access_key='***********')
        self.cache_client = session.client('ecr', region_name='us-west-2')

    def push(self, key, val):
        self.cache_client.tag_resource(
            resourceArn='arn:aws:ecr:us-west-2:181756629255:repository/webserver',
            tags=[
                {
                    'Key': key,
                    'Value': str(val)
                },
            ]
        )

    def pull(self, key):
        tags = self.cache_client.list_tags_for_resource(
            resourceArn='arn:aws:ecr:us-west-2:181756629255:repository/webserver'
        )
        for tag in tags['tags']:
            if 'Key' in tag and tag['Key'] == key:
                return tag['Value']
        return '0'

    def delete(self, key):
        self.cache_client.delete(key)
