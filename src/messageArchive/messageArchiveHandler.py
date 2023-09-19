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
from datetime import datetime
import boto3
import os
import redis
import base64

from template_loader import get_lambda_template
from exception_handler import capture_except, post_to_dlq
import common_fields

SEPARATOR = "/"

REDIS_HOST = os.environ[common_fields.OS_REDIS_HOST]
REDIS_PORT = int(os.environ[common_fields.OS_REDIS_PORT])
REDIS_AUTH = os.environ[common_fields.OS_REDIS_AUTH]
REDIS_USER = os.environ[common_fields.OS_REDIS_USER]
REDIS_SECRET_ARN = os.environ[common_fields.OS_REDIS_SECRET_ARN]

S3_BUCKET = os.environ[common_fields.OS_ARCHIVE_BUCKET]
DLQ_URL = os.environ[common_fields.OS_DEAD_LETTER]

PATH_PATTERN = f"%Y{SEPARATOR}%m{SEPARATOR}%d{SEPARATOR}%H{SEPARATOR}%M{SEPARATOR}%S"

redisClient = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    ssl=True,
    password=REDIS_AUTH,
    username=REDIS_USER,
)

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    try:
        response = get_lambda_template()

        redis_key = event[common_fields.MESSAGE_STORAGE_CONTEXT][
            common_fields.MESSAGE_REDIS_REFERENCE
        ]["key"]
        raw_payload = getPayload(redis_key)
        binary_payload = base64.b64decode(raw_payload)

        timestamp = datetime.strptime(
            event[common_fields.MESSAGE_META_DATA][common_fields.MESSAGE_DATE_TIME],
            "%Y-%m-%d %H:%M:%S.%f",
        )
        s3_key = f'{timestamp.strftime(PATH_PATTERN)}{SEPARATOR}{event["messageID"]}'

        s3_client.put_object(Body=binary_payload, Bucket=S3_BUCKET, Key=s3_key)

        print(f"Payload Written to S3: {len(binary_payload)} bytes")

        event[common_fields.MESSAGE_STORAGE_CONTEXT][common_fields.MESSAGE_S3_REFERENCE][
            "bucket"
        ] = S3_BUCKET
        event[common_fields.MESSAGE_STORAGE_CONTEXT][common_fields.MESSAGE_S3_REFERENCE][
            "key"
        ] = s3_key

        event[common_fields.MESSAGE_STORAGE_CONTEXT][common_fields.MESSAGE_PERSISTENCE][
            "S3"
        ] = True

        response["body"] = event

        print(response)

        return response
    except:
        except_data = capture_except()
        sqs_message = {
            "exception": except_data,
            "event": event,
            "message": "Failed to archive message payload",
        }
        post_to_dlq(sqs_message, DLQ_URL)

        response = get_lambda_template()
        response["statusCode"] = 500
        response["body"] = sqs_message
        return response


def getPayload(transaction_id):
    return redisClient.get(
        name=transaction_id,
    )
