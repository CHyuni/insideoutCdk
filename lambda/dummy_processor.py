import json
import boto3
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    try:
        body = json.loads(event['body'])
        filename = body.get('filename')
        emotion = body.get('emotion')
        
        # DynamoDB에 저장
        table = dynamodb.Table(os.environ['TABLE_NAME'])
        response = table.put_item(
            Item={
                'filename': filename,
                'label': emotion,
                'count': 1
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': 'Emotion recorded'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': str(e)})
        }