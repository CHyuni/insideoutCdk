import boto3
import random
import json
import os
from botocore.config import Config
from botocore.exceptions import ClientError

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
dynamodb = boto3.resource('dynamodb')

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(body)
    }

def handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return create_response(200, '')

    bucket_name = os.environ['PLAY_BUCKET']
    
    try:
        # playBucket에서 랜덤 파일 선택
        response = s3.list_objects_v2(Bucket=bucket_name)
        all_files = [obj['Key'] for obj in response.get('Contents', [])]
        selected_file = random.choice(all_files)
        
        # 파일 이름에서 정답 추출 (3번째 부분)
        answer = selected_file.split('-')[2] if len(selected_file.split('-')) > 2 else ''
        
        # 선택된 파일에 대한 pre-signed URL 생성
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name, 'Key': selected_file},
                                        ExpiresIn=300,
                                        HttpMethod='GET')
        
        return create_response(200, {
            'audioUrl': url,
            'answer': answer,
            'fileName': selected_file  # 디버깅을 위해 파일 이름도 포함
        })
    except ClientError as e:
        return create_response(500, {'error': str(e)})