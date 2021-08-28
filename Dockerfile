FROM python

RUN pip install boto3 elasticache_auto_discovery pymemcache redis

COPY . /

EXPOSE 8080
EXPOSE 6379
EXPOSE 11211

CMD python webServer.py