FROM python:3.7

EXPOSE 8080

RUN pip3 install flask aws-xray-sdk boto3 requests

RUN curl -o daemon.zip https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-linux-3.x.zip
RUN unzip daemon.zip && cp xray /usr/bin/xray

COPY app.py /

COPY cfg.yaml /

COPY /startup.sh /

ENTRYPOINT ["/startup.sh"]


