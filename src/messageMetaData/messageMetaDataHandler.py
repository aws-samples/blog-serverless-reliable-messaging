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
        transactionID = event[common_fields.MESSAGE_TRANSACTION_GUID]
        message_timestamp = datetime.strptime(
            event[common_fields.MESSAGE_META_DATA][common_fields.MESSAGE_DATE_TIME],
            "%Y-%m-%d %H:%M:%S.%f",
        )

        response = get_lambda_template()

        event[common_fields.MESSAGE_STORAGE_CONTEXT][
            common_fields.MESSAGE_METADATA_REFERENCE
        ]["dynamoDbTableName"] = DYNAMO_DB_TABLE_NAME
        event[common_fields.MESSAGE_STORAGE_CONTEXT][
            common_fields.MESSAGE_METADATA_REFERENCE
        ]["primaryKey"] = transactionID

        event[common_fields.MESSAGE_STORAGE_CONTEXT][common_fields.MESSAGE_PERSISTENCE][
            "metaData"
        ] = True

        response["body"] = event

        milliseconds = int(round(message_timestamp.timestamp() * 1000))

        table.put_item(
            Item={
                "transcationID": transactionID,
                "timestampValue": milliseconds,
                "metaData": event,
            }
        )

        # print(response)

        return response
    except:
        except_data = capture_except()
        sqs_message = {"exception": except_data, "event": event, "message": "Failed to write metadata for message"}
        post_to_dlq(sqs_message, DLQ_URL)
        
        response = get_lambda_template()
        response["statusCode"] = 500
        response["body"] = sqs_message
        return response
        