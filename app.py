#!/usr/local/bin/python3 /app.py

from flask import Flask

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

import boto3

import sys
import signal
import os
import requests
import json
import errno

import logging

patch_all()

app = Flask(__name__)


def cleanup(signum, frame):
    """
    Called on a terminate signal.
    Cleanup anything we need to before we depart this mortal coil.

    https://docs.aws.amazon.com/cli/latest/reference/ecs/stop-task.html

    This handler is in anticipation of a SIGTERM when 'docker stop' is sent.

    :return:
        DOES NOT RETURN
    """
    logging.info("shutdown signal %s received, cleanup and exit", signum)
    sys.exit()

# use a decorator to create a subsegment
@xray_recorder.capture('get_file')
def get_file():
    """
    demonstrate intentional error

    :return:
    """
    result = None
    try:
        # add request context information to the trace for this subsegment
        document = xray_recorder.current_subsegment()
        document.put_annotation("filename", "hello.txt")

        request = {'requestId': '123-123', 'value1': 20}
        document.put_metadata('key', request, 'namespace')

        # intentional file not found error to demonstrate x-ray
        s3 = boto3.resource('s3')
        result = s3.Object('dummybucket', 'hello.txt').download_file('/tmp/hello.txt')
    except Exception as e:
        logging.error("download failed: %s", str(e))
    finally:
        if result is None:
            sub_segment = xray_recorder.current_subsegment()
            sub_segment.apply_status_code(500)
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), 'hello.txt')


@app.route('/')
def hello_world():
    # Start a segment
    segment = xray_recorder.begin_segment('hello_world')

    # Start a subsegment
    subsegment = xray_recorder.begin_subsegment('get-s3-data-files')

    version = "version-05"

    cluster_name = 'not_set'

    resp = {}
    data = {}

    try:
        logging.info("metadata_uri:" + os.environ['ECS_CONTAINER_METADATA_URI'])

        resp = requests.get(url=os.environ['ECS_CONTAINER_METADATA_URI'] + '/task')
        data = resp.json()

    except Exception as e:
        logging.error("error getting metadata:" + str(e))

    if 'Cluster' in data:
        cluster_arn = data['Cluster']
        cluster_list = cluster_arn.split('/')
        cluster_name = cluster_list[1]
    else:
        cluster_name = 'not_set'

    logging.info("cluster:" + cluster_name)

    client = boto3.client('s3')
    response = client.list_buckets()

    logging.info("s3 response: %s", response['Owner']['DisplayName'])

    # Close the subsegment and segment
    xray_recorder.end_subsegment()

    try:
        get_file()
    except Exception as e:

        logging.error("get_File error")

    xray_recorder.end_segment()

    return json.dumps({"version": version}), 500


if __name__ == "__main__":

    # make preparations for termination
    signal.signal(signal.SIGTERM, cleanup)

    logging.basicConfig(level=logging.INFO)

    xray_recorder.configure(sampling=False)

    app.run(host="0.0.0.0", port=8080, threaded=False)
