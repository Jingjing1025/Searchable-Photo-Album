import boto3
import re
import requests
import time
import json
from urllib.parse import unquote_plus
from requests_aws4auth import AWS4Auth

region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = '' # the Amazon ES domain, including https://
index = 'photos'
type = '_doc'
url = host + '/' + index + '/' + type

headers = { "Content-Type": "application/json" }

s3 = boto3.client('s3')
rek = boto3.client('rekognition')

def searchFromES(q):
    query = {
        "size": 25,
        "query": {
            "match": {
                "labels": q
            }
        }
    }

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }
    
    # print(json.dumps(query))

    # Make the signed HTTP request
    try:
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    except:
        print("failed connection")

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = r.text
    found_results = json.loads(r.text)

    photos = []
    for hit in found_results['hits']['hits']:
        photos.append(hit['_source']['objectKey'])

    return photos
    

# Lambda execution starts here
def lambda_handler(event, context):
    
    print (event)

    for record in event['Records']:
        
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        print (bucket)
        photo = unquote_plus(record['s3']['object']['key'])
        print (photo)

        response = rek.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10)
        
        labels=[]
        for label in response['Labels']:
            labels.append(label['Name'])
        
        print(labels)
        
        timestamp = int(time.time())
            
        document = {
            "objectKey": photo,
            "bucket": bucket, 
            "createdTimestamp": str(timestamp),
            "labels": labels
        }
        r = requests.post(url, auth=awsauth, data=json.dumps(document), headers=headers)
        print(r.json())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda function!')
    }
