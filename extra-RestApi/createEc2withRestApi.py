# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
#
# ABOUT THIS PYTHON SAMPLE: This sample is part of the AWS General Reference 
# Signing AWS API Requests top available at
# https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
#

# AWS Version 4 signing example

# EC2 API (DescribeRegions)

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a GET request and passes the signature
# in the Authorization header.
import sys, os, base64, datetime, hashlib, hmac 
import requests # pip install requests

# ************* REQUEST VALUES *************
method = 'POST'
service = 'ec2'
host = 'ec2.amazonaws.com'
region = 'us-east-1'
timeout_interval = 60
endpoint = 'https://ec2.amazonaws.com'
request_parameters = 'Action=RunInstances' # Version can be specified

# Build request
request_parameters +=  '&ImageId=ami-047a51fa27710816e'
request_parameters +=  '&InstanceType=t2.micro'
request_parameters +=  '&MaxCount=1'
request_parameters +=  '&MinCount=1'

print("Request Parameters:")
print(request_parameters)


# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
from creds.keys import access_key, secret_key
access_key = access_key #os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = secret_key #os.environ.get('AWS_SECRET_ACCESS_KEY')
if access_key is None or secret_key is None:
    print('No access key is available.')
    sys.exit()

# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


# ************* TASK 1: CREATE A CANONICAL REQUEST *************
# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# Step 1 is to define the verb (GET, POST, etc.)--already done.

# Step 2: Create canonical URI--the part of the URI from domain to query 
# string (use '/' if no path)
canonical_uri = '/' 

# Step 3: Create the canonical query string. In this example (a GET request),
# request parameters are in the query string. Query string values must
# be URL-encoded (space=%20). The parameters must be sorted by name.
# For this example, the query string is pre-formatted in the request_parameters variable.
canonical_querystring = request_parameters

# Step 4: Create the canonical headers and signed headers. Header names
# must be trimmed and lowercase, and sorted in code point order from
# low to high. Note that there is a trailing \n.
canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'

# Step 5: Create the list of signed headers. This lists the headers
# in the canonical_headers list, delimited with ";" and in alpha order.
# Note: The request can include any headers; canonical_headers and
# signed_headers lists those that you want to be included in the 
# hash of the request. "Host" and "x-amz-date" are always required.
signed_headers = 'host;x-amz-date'

# Step 6: Create payload hash (hash of the request body content). For GET
# requests, the payload is an empty string ("").
payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()

# Step 7: Combine elements to create canonical request
canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash


# ************* TASK 2: CREATE THE STRING TO SIGN*************
# Match the algorithm to the hashing algorithm you use, either SHA-1 or
# SHA-256 (recommended)
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

# ************* TASK 3: CALCULATE THE SIGNATURE *************
# Create the signing key using the function defined above.
signing_key = getSignatureKey(secret_key, datestamp, region, service)

# Sign the string_to_sign using the signing_key
signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()


# ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# The signing information can be either in a query string value or in 
# a header named Authorization. This code shows how to use a header.
# Create authorization header and add to request headers

authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

import urllib

canonical_querystring += f"&X-Amz-Algorithm={algorithm}"
canonical_querystring += f"&X-Amz-Credential={urllib.parse.quote(access_key + '/' + credential_scope, safe = '')}"
canonical_querystring += f"&X-Amz-Date={amzdate}"
canonical_querystring += f"&X-Amz-Expires={timeout_interval}"
canonical_querystring += f"&X-Amz-SignedHeaders={signed_headers}"
canonical_querystring += f"&X-Amz-Signature={signature}"

# The request can include any headers, but MUST include "host", "x-amz-date", 
# and (for this scenario) "Authorization". "host" and "x-amz-date" must
# be included in the canonical_headers and signed_headers, as noted
# earlier. Order here is not significant.
# Python note: The 'host' header is added automatically by the Python 'requests' library.
headers = {'x-amz-date':amzdate} #, 'Authorization':authorization_header}


# ************* SEND THE REQUEST *************
request_url = endpoint + '?' + canonical_querystring

print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
print('Request URL = ' + request_url)
r = requests.get(request_url, headers=headers)

print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
print('Response code: %d\n' % r.status_code)
print(r.text)
 




# # Based on a script form Amazon with the following header:
# # 
# # Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# #
# # This file is licensed under the Apache License, Version 2.0 (the "License").
# # You may not use this file except in compliance with the License. A copy of the
# # License is located at
# #
# # http://aws.amazon.com/apache2.0/
# #
# # This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# # OF ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.

# # AWS Version 4 signing example

# # DynamoDB API (CreateTable)

# # See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# # This version makes a POST request and passes request parameters
# # in the body (payload) of the request. Auth information is passed in
# # an Authorization header.

# # Also used example requests from https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RunInstances.html

# # https://ec2.amazonaws.com/?Action=RunInstances
# # &ImageId=ami-31814f58
# # &InstanceType=t2.large
# # &MaxCount=2
# # &MinCount=1
# # &KeyName=my-key-pair
# # &SubnetId=subnet-b2a249da
# # &TagSpecification.1.ResourceType=instance
# # &TagSpecification.1.Tag.1.Key=webserver
# # &TagSpecification.1.Tag.1.Value=production
# # &TagSpecification.2.ResourceType=volume
# # &TagSpecification.2.Tag.1.Key=cost-center
# # &TagSpecification.2.Tag.1.Value=cc123
# # &AUTHPARAMS


# import sys, os, base64, datetime, hashlib, hmac 
# import requests # pip install requests

# # ************* REQUEST VALUES *************
# method = 'POST'
# service = 'ec2'
# host = 'ec2.us-east-1.amazonaws.com'
# region = 'us-east-1'
# endpoint = 'https://ec2.us-east-1.amazonaws.com/'
# # POST requests use a content type header. For DynamoDB,
# # the content is JSON.
# content_type = 'application/x-amz-json-1.0'
# # DynamoDB requires an x-amz-target header that has this format:
# #     DynamoDB_<API version>.<operationName>
# # amz_target = 'DynamoDB_20120810.CreateTable'

# # Request parameters for CreateTable--passed in a JSON block.
# request_parameters =  '{'
# request_parameters +=  '"ImageId": "ami-047a51fa27710816e",'
# request_parameters +=  '"InstanceType": "t2.micro",'
# request_parameters +=  '"MaxCount": 1,'
# request_parameters +=  '"MinCount": 1'
# request_parameters +=  '}'
# print("Request Parameters:")
# print(request_parameters)

# # Key derivation functions. See:
# # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
# def sign(key, msg):
#     return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

# def getSignatureKey(key, date_stamp, regionName, serviceName):
#     kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
#     kRegion = sign(kDate, regionName)
#     kService = sign(kRegion, serviceName)
#     kSigning = sign(kService, 'aws4_request')
#     return kSigning

# # Read AWS access key from env. variables or configuration file. Best practice is NOT
# # to embed credentials in code.
# from creds.keys import access_key, secret_key
# access_key = access_key #os.environ.get('AWS_ACCESS_KEY_ID')
# secret_key = secret_key #os.environ.get('AWS_SECRET_ACCESS_KEY')
# if access_key is None or secret_key is None:
#     print('No access key is available.')
#     sys.exit()

# # Create a date for headers and the credential string
# t = datetime.datetime.utcnow()
# amz_date = t.strftime('%Y%m%dT%H%M%SZ')
# date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


# # ************* TASK 1: CREATE A CANONICAL REQUEST *************
# # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# # Step 1 is to define the verb (GET, POST, etc.)--already done.

# # Step 2: Create canonical URI--the part of the URI from domain to query 
# # string (use '/' if no path)
# canonical_uri = '/'

# ## Step 3: Create the canonical query string. In this example, request
# # parameters are passed in the body of the request and the query string
# # is blank.
# canonical_querystring = ''

# # Step 4: Create the canonical headers. Header names must be trimmed
# # and lowercase, and sorted in code point order from low to high.
# # Note that there is a trailing \n.
# canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' # + 'x-amz-target:' + amz_target + '\n' # needed for DynamoDB

# # Step 5: Create the list of signed headers. This lists the headers
# # in the canonical_headers list, delimited with ";" and in alpha order.
# # Note: The request can include any headers; canonical_headers and
# # signed_headers include those that you want to be included in the
# # hash of the request. "Host" and "x-amz-date" are always required.
# # For DynamoDB, content-type and x-amz-target are also required.
# signed_headers = 'content-type;host;x-amz-date' #;x-amz-target'

# # Step 6: Create payload hash. In this example, the payload (body of
# # the request) contains the request parameters.
# payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

# # Step 7: Combine elements to create canonical request
# canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash


# # ************* TASK 2: CREATE THE STRING TO SIGN*************
# # Match the algorithm to the hashing algorithm you use, either SHA-1 or
# # SHA-256 (recommended)
# algorithm = 'AWS4-HMAC-SHA256'
# credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
# string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

# # ************* TASK 3: CALCULATE THE SIGNATURE *************
# # Create the signing key using the function defined above.
# signing_key = getSignatureKey(secret_key, date_stamp, region, service)

# # Sign the string_to_sign using the signing_key
# signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()


# # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# # Put the signature information in a header named Authorization.
# authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

# # For DynamoDB, the request can include any headers, but MUST include "host", "x-amz-date",
# # "x-amz-target", "content-type", and "Authorization". Except for the authorization
# # header, the headers must be included in the canonical_headers and signed_headers values, as
# # noted earlier. Order here is not significant.
# # # Python note: The 'host' header is added automatically by the Python 'requests' library.
# headers = {'Content-Type':content_type,
#            'X-Amz-Date':amz_date,
#            'Authorization':authorization_header}
#         #    'X-Amz-Target':amz_target, 


# # ************* SEND THE REQUEST *************
# print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
# print('Request URL = ' + endpoint)

# r = requests.post(endpoint, data=request_parameters, headers=headers)

# print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
# print('Response code: %d\n' % r.status_code)
# print(r.text)
 


