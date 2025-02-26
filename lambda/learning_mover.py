import json
import boto3
import os

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

DUMMY_BUCKET = os.environ['DUMMY_BUCKET']
LEARNING_BUCKET = os.environ['LEARNING_BUCKET']
TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            count = int(new_image['count']['N'])
            filename = new_image['filename']['S']
            
            if count == 10:
                # Move file from dummy to learning bucket
                copy_source = {
                    'Bucket': DUMMY_BUCKET,
                    'Key': filename
                }
                s3.copy(copy_source, LEARNING_BUCKET, filename)
                s3.delete_object(Bucket=DUMMY_BUCKET, Key=filename)
                
                # Delete all items with the same filename from DynamoDB
                response = dynamodb.query(
                    TableName=TABLE_NAME,
                    KeyConditionExpression='filename = :filename',
                    ExpressionAttributeValues={
                        ':filename': {'S': filename}
                    }
                )
                
                for item in response['Items']:
                    dynamodb.delete_item(
                        TableName=TABLE_NAME,
                        Key={
                            'filename': {'S': item['filename']['S']},
                            'label': {'S': item['label']['S']}
                        }
                    )

    return {
        'statusCode': 200,
        'body': json.dumps('Processing completed')
    }