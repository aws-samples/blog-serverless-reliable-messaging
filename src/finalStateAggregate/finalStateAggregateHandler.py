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

from template_loader import get_lambda_template
from exception_handler import capture_except, post_to_dlq
import common_fields

DYNAMO_DB_TABLE_NAME = os.environ[common_fields.OS_DYNAMODB_TABLE]
DLQ_URL = os.environ[common_fields.OS_DEAD_LETTER]

table = boto3.resource("dynamodb").Table(DYNAMO_DB_TABLE_NAME)


def lambda_handler(event, context):
    try:
        payload = get_lambda_template()

        for record in event:
            if record["message"] == "Data workflow started":
                message_timestamp = datetime.strptime(
                    record[common_fields.MESSAGE_META_DATA][
                        common_fields.MESSAGE_DATE_TIME
                    ],
                    "%Y-%m-%d %H:%M:%S.%f",
                )
                milliseconds = int(round(message_timestamp.timestamp() * 1000))

                payload = table.get_item(
                    Key={
                        "transcationID": record[common_fields.MESSAGE_TRANSACTION_GUID],
                        "timestampValue": milliseconds,
                    }
                )["Item"]["metaData"]

        print(payload)

        for record in event:
            if record["message"] == "Data workflow started":
                message_timestamp = datetime.strptime(
                    record[common_fields.MESSAGE_META_DATA][common_fields.MESSAGE_DATE_TIME],
                    "%Y-%m-%d %H:%M:%S.%f",
                )
            elif record["message"] == "S3 Archive Completed":
                payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_S3_REFERENCE
                ] = record[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_S3_REFERENCE
                ]
                payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_PERSISTENCE
                ]["S3"] = True
            elif record["message"] == "Meta Data archive completed":
                payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_METADATA_REFERENCE
                ] = record[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_METADATA_REFERENCE
                ]
                payload[common_fields.MESSAGE_STORAGE_CONTEXT][
                    common_fields.MESSAGE_PERSISTENCE
                ]["metaData"] = True

        print(payload)

        milliseconds = int(round(message_timestamp.timestamp() * 1000))

        table.put_item(
            Item={
                "transcationID": payload[common_fields.MESSAGE_TRANSACTION_GUID],
                "timestampValue": milliseconds,
                "metaData": payload,
            }
        )

        # You could delete the redis cached copy of the message here

        return payload
    except:
        except_data = capture_except()
        sqs_message = {
            "exception": except_data,
            "event": event,
            "message": "Failed to write final state for message",
        }
        post_to_dlq(sqs_message, DLQ_URL)

        response = get_lambda_template()
        response["statusCode"] = 500
        response["body"] = sqs_message
        return response
