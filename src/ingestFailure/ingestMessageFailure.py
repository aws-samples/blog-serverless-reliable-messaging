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
from exception_handler import capture_except, post_to_dlq
from template_loader import get_lambda_template
import common_fields
import boto3
import json
import uuid
import os

S3_TARGET = os.environ[common_fields.OS_FAILURE_BUCKET]
DLQ_URL = os.environ[common_fields.OS_DEAD_LETTER]

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
    
def lambda_handler(event, context):
    try:
        fail_guid = str(uuid.uuid4())
        string_payload = json.dumps(event, indent=4)
        s3_client.put_object(Body=string_payload, Bucket=S3_TARGET, Key=fail_guid)

        json_data = {
            "message": "A payload failed to be ingested",
            "fail_guid": fail_guid,
            "written_to_s3_bucket": S3_TARGET
        }
        post_to_dlq(json_data, DLQ_URL)
        
        return respond(json_data)
    except:
        except_data = capture_except()
        sqs_message = {
            "message": "Ingestion failure handler failed.",
            "exception": except_data,
            "event": event
        }
        post_to_dlq(sqs_message, DLQ_URL)
        return respond(sqs_message)
        
        
def respond(payload):
    response = get_lambda_template()
    response["body"] = json.dumps(payload)
    response["statusCode"] = 500
    
    return response