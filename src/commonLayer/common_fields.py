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

#OS Variables
OS_ARCHIVE_BUCKET = 'S3ArchiveBucketName'
OS_FAILURE_BUCKET = 'FailBucket'
OS_DEAD_LETTER = 'DLQUrl'
OS_REDIS_HOST = 'RedisEndpointAddress'
OS_REDIS_PORT = 'RedisEndpointPort'
OS_REDIS_AUTH = 'RedisAuthToken'
OS_REDIS_USER = 'RedisUsername'
OS_REDIS_SECRET_ARN = 'RedisSecretArn'
OS_STEP_FUNC_ARN = 'StepFunctionArn'
OS_LAMBDA_NAME = 'FailLambda'
OS_DYNAMODB_TABLE = 'MetaDataTable'

# fields from incoming request
INCOMING_REQUEST_CONTEXT = 'requestContext'
INCOMING_TRANSACTION_ID = 'sourceTransactionID'
INCOMING_SYSTEM_ID = 'sourceSystemID'
INCOMING_PAYLOAD = 'messagePayload'

# Fields in internal data structure
MESSAGE_TRANSACTION_GUID = 'messageID'
MESSAGE_META_DATA = 'messageMetaData'
MESSAGE_TYPE = 'messageType'
MESSAGE_DATE_TIME = 'dateTime'
MESSAGE_CONTEXT = 'messageSecurityContext'
MESSAGE_STORAGE_CONTEXT = 'storageContext'
MESSAGE_REDIS_REFERENCE = 'redisReference'
MESSAGE_METADATA_REFERENCE = 'metaDataReference'
MESSAGE_S3_REFERENCE = 'S3Reference'
MESSAGE_PERSISTENCE = 'persistence'

STANDARD_ENCODING = 'utf-8'