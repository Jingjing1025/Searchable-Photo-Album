import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

client = boto3.client('lex-runtime')

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = ''
index = 'photos'
url = host + '/' + index + '/_search'

headers = { "Content-Type": "application/json" }

def lambda_handler(event, context):
    print("event: ", event)
    searchQuery = event['q']
    client = boto3.client('lex-runtime')
    
    response = client.post_text(
        botName='searchKeyWords',
        botAlias='test',
    
        userId='string',
        
        sessionAttributes={
            'string': 'string'
        },
        requestAttributes={
            'string': 'string'
        },
        
        inputText = searchQuery
    )
    slots = []
    if 'slots' in response:
        for k, v in response['slots'].items():
            if v is not None:
                slots.append(v)
    #print (slots)
    res = elasticSearch(slots)
    print(res)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'photos_result': res,
        'headers': {
    "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
    "Access-Control-Allow-Credentials" : True, # Required for cookies, authorization headers with HTTPS 
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
  }
    }
    
    
def elasticSearch(slots):
    
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    print("slots: ", slots)
    
    query = {
        "query": {
        "bool": {
            "filter": {
                "terms": {
                    "labels": slots
                }
            }
        }
        }
    }

    # Make the signed HTTP request
    found_results = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    photos_result = []
    try:
        res = json.loads(found_results.text)
        for hit in res['hits']['hits']:
            photos_result.append(hit['_source']['objectKey'])
    except:
        return photos_result

    return photos_result
    