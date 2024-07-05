import boto3
import random
import json
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    bucket_name = os.environ['DUMMY_BUCKET']
    table_name = os.environ['TABLE_NAME']
    table = dynamodb.Table(table_name)
    
    # dummyBucket에서 랜덤 파일 선택
    response = s3.list_objects_v2(Bucket=bucket_name)
    all_files = [obj['Key'] for obj in response.get('Contents', [])]
    selected_file = random.choice(all_files)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'file': selected_file
        })
    }