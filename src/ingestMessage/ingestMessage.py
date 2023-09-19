#
# MIT No Attribution
#
# Copyright 2023 Amazon.com, Inc. or its affiliates.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.#
from botocore.exceptions import ClientError
import redis
import json
import uuid
import logging
import os
import datetime
import boto3

from template_loader import get_lambda_template, get_internal_template
from exception_handler import capture_except, post_to_dlq
import common_fields

logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ[common_fields.OS_REDIS_HOST]
REDIS_PORT = int(os.environ[common_fields.OS_REDIS_PORT])
REDIS_AUTH = os.environ[common_fields.OS_REDIS_AUTH]
REDIS_USER = os.environ[common_fields.OS_REDIS_USER]
REDIS_SECRET_ARN = os.environ[common_fields.OS_REDIS_SECRET_ARN]

STEP_FUNC_ARN = os.environ[common_fields.OS_STEP_FUNC_ARN]
DLQ_URL = os.environ[common_fields.OS_DEAD_LETTER]
LAMBDA_NAME = os.environ[common_fields.OS_LAMBDA_NAME]

redisClient = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    ssl=True,
    password=REDIS_AUTH,
    username=REDIS_USER,
)

step_client = boto3.client("stepfunctions")
lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    try:
        # construct response
        response = get_lambda_template()
        payload = get_internal_template()

        body = {}
        body[common_fields.MESSAGE_TRANSACTION_GUID] = str(uuid.uuid4())

        # parse body
        if "body" in event:
            content = event["body"]
            if isinstance(content, str):
                content = json.loads(content)

            payload[common_fields.MESSAGE_META_DATA] = content[
                common_fields.MESSAGE_META_DATA
            ].copy()

            if common_fields.INCOMING_REQUEST_CONTEXT in event.keys():
                payload[common_fields.MESSAGE_CONTEXT] = event[
                    common_fields.INCOMING_REQUEST_CONTEXT
                ]
            else:
                payload[common_fields.MESSAGE_CONTEXT] = {"context": None}

            payload[common_fields.MESSAGE_TRANSACTION_GUID] = body[
                common_fields.MESSAGE_TRANSACTION_GUID
            ]

            payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                common_fields.MESSAGE_REDIS_REFERENCE
            ]["server"] = REDIS_HOST
            payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                common_fields.MESSAGE_REDIS_REFERENCE
            ]["port"] = REDIS_PORT
            payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                common_fields.MESSAGE_REDIS_REFERENCE
            ]["key"] = body[common_fields.MESSAGE_TRANSACTION_GUID]

            string_payload = json.dumps(payload)

            storePayload(
                body[common_fields.MESSAGE_TRANSACTION_GUID],
                content[common_fields.INCOMING_PAYLOAD],
            )
            sendNotice(string_payload)
        else:
            raise Exception("Malformed input ...")

        response["body"] = json.dumps(body)

        return response
    except:
        except_data = capture_except()
        sqs_message = {"exception": except_data, "event": event}
        return invoke_function(LAMBDA_NAME, sqs_message)


def invoke_function(function_name, function_params, get_log=False):
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(function_params),
            LogType="Tail" if get_log else "None",
        )
        
        full_body = json.loads(response['Payload'].read())

        return full_body
    except ClientError:
        exception = capture_except()
        print(exception)
        if common_fields.INCOMING_PAYLOAD in function_params["event"]:
            del function_params["event"][common_fields.INCOMING_PAYLOAD]

        post_to_dlq(function_params, DLQ_URL)


def storePayload(transaction_id, payload):
    redisClient.setex(
        transaction_id,
        datetime.timedelta(minutes=60),
        payload,
    )
    return


def sendNotice(payload):
    print(STEP_FUNC_ARN)
    step_client.start_execution(stateMachineArn=STEP_FUNC_ARN, input=payload)

    return


if __name__ == "__main__":
    with open("test_message.json", "r") as f:
        test_message = f.read()
        test_message = json.loads(test_message)
        lambda_handler(test_message, {})
