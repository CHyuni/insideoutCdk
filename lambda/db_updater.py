import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    table_name = os.environ['TABLE_NAME']
    table = dynamodb.Table(table_name)
    
    body = json.loads(event['body'])
    file_name = body['file_name']
    user_answer = body['user_answer']
    
    # DB에 결과 추가
    response = table.put_item(
        Item={
            'filename': file_name,
            'label': user_answer
        }
    )
    
    # 레이블 카운트 확인 및 업데이트
    count_response = table.query(
        KeyConditionExpression='filename = :fn AND label = :lb',
        ExpressionAttributeValues={
            ':fn': file_name,
            ':lb': user_answer
        }
    )
    
    count = len(count_response.get('Items', []))
    
    if count >= 10:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'move_file': True,
                'file_name': file_name
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'move_file': False
            })
        }