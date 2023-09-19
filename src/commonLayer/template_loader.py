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
from copy import deepcopy

INTERNAL_MESSAGE = {
    "messageID": None,
    "messageMetaData": {},
    "storageContext": {
        "redisReference": {"server": None, "port": None, "key": None},
        "S3Reference": {"bucket": None, "key": None},
        "metaDataReference": {"dynamoDbTableName": None, "primaryKey": None},
        "persistence": {"S3": False, "metaData": False},
    },
    "messageSecurityContext": {},
}

LAMBDA_RESPONSE_TEMPLATE = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }
}

def get_internal_template():
    return deepcopy(INTERNAL_MESSAGE)


def get_lambda_template():
    return deepcopy(LAMBDA_RESPONSE_TEMPLATE)
