FROM python

RUN pip install boto3

COPY . /

EXPOSE 8080

CMD python webServer.py