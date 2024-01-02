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
import requests
import json

BASE_URL = "<Your API Gateway URL here (IngestMessageApi)>"
security_key = "<Your API Key here>"

json_payload = None
with open('test_client/test_api_message.json', 'r') as f:
    json_payload = json.load(f)
    
r = requests.post(BASE_URL, json=json_payload, headers={'x-api-key': security_key})    

print(r.status_code)
if r.status_code == requests.codes.ok:
    print("Success")
    print(json.dumps(r.json(), indent=2))
    print(r.headers.get('content-type'))
    print(json.dumps(dict(r.headers), indent=2))