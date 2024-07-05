import boto3
import json
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    dummy_bucket = os.environ['DUMMY_BUCKET']
    learning_bucket = os.environ['LEARNING_BUCKET']
    table_name = os.environ['TABLE_NAME']
    table = dynamodb.Table(table_name)
    
    body = json.loads(event['body'])
    file_name = body['file_name']
    
    # 파일 복사
    s3.copy_object(
        CopySource={'Bucket': dummy_bucket, 'Key': file_name},
        Bucket=learning_bucket,
        Key=file_name
    )
    
    # 원본 파일 삭제
    s3.delete_object(Bucket=dummy_bucket, Key=file_name)
    
    # DB에서 관련 항목 삭제
    table.delete_item(
        Key={
            'filename': file_name
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('File moved and DB updated successfully')
    }