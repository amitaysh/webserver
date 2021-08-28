FROM python

RUN pip install boto3 elasticache_auto_discovery pymemcache redis

COPY . /

EXPOSE 8080

CMD python webServer.py