import logging
import json
import os
import random
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from urllib.parse import quote
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache'    
        },
        'body': json.dumps(body)
    }

def handler(event, context):
    logger.info(f"Received event: {event}")

    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, '')

    play_bucket = os.environ['PLAY_BUCKET']
    dummy_bucket = os.environ['DUMMY_BUCKET']

    try:
        body = json.loads(event['body'])
        action = body.get('action')

        if action == 'initialize':
            attempt = body.get('attempt', 0)
            bucket_name = dummy_bucket if attempt == 1 else play_bucket

            response = s3.list_objects_v2(Bucket=bucket_name)
            all_files = [obj['Key'] for obj in response.get('Contents', [])]

            if not all_files:
                return create_response(404, {'error': 'No audio files found in the bucket'})
            selected_file = random.choice(all_files)

            url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name, 'Key': selected_file},
                                            ExpiresIn=600,
                                            HttpMethod='GET')

            encoded_url = quote(url, safe=':/?=&')

            result = {
                'audioUrl': encoded_url,
                'fileName': selected_file
            }
            return create_response(200, result)

        elif action == 'check':
            file_name = body.get('fileName')
            user_answer = body.get('answer', '').lower()
            attempt = body.get('attempt', 0)

            if attempt == 1:  # 4번째 시도 (인덱스는 0부터 시작하므로 3)
                try:
                    response = table.update_item(
                        Key={
                            'filename': file_name,
                            'label': user_answer
                        },
                        UpdateExpression="SET #count = if_not_exists(#count, :zero) + :inc, #timestamp = :timestamp",
                        ExpressionAttributeNames={
                            '#count': 'count',
                            '#timestamp': 'timestamp'
                        },
                        ExpressionAttributeValues={
                            ':inc': 1,
                            ':zero': 0,
                            ':timestamp': datetime.now().isoformat()
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    
                    updated_count = int(response['Attributes'].get('count', 1))
                    
                    result = {
                        'correct': True,
                        'message': 'Final test completed',
                        'count': updated_count,
                        'finalTest': True
                    }

                    # count가 10 이상이면 클라이언트에 알림
                    if updated_count >= 10:
                        result['reachedThreshold'] = True

                    return create_response(200, result)
                
                except ClientError as e:
                    logger.error(f"Error updating DynamoDB: {str(e)}")
                    return create_response(500, {'error': 'Error updating database', 'finalTest': True})
            else:
                bucket_name = play_bucket
                try:
                    object_info = s3.head_object(Bucket=bucket_name, Key=file_name)
                    correct_answer = object_info['Metadata'].get('x-amz-meta-answer', '').lower()
                    is_correct = user_answer == correct_answer
                    return create_response(200, {'correct': is_correct, 'finalTest': False})
                except ClientError as e:
                    logger.error(f"Error accessing S3: {str(e)}")
                    return create_response(500, {'error': 'Error checking answer', 'finalTest': False})

        else:
            return create_response(400, {'error': 'Invalid action'})

    except ClientError as e:
        error_response = create_response(500, {'error': str(e)})
        logger.error(f"Error occurred: {error_response}")
        return error_response
    except Exception as e:
        error_response = create_response(500, {'error': f'Unexpected error: {str(e)}'})
        logger.error(f"Unexpected error occurred: {error_response}")
        return error_response