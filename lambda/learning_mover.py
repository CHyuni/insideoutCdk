import boto3
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    try:
        table = dynamodb.Table(os.environ['TABLE_NAME'])
        
        # DynamoDB 스캔 (실제로는 더 효율적인 쿼리 방법을 사용해야 함)
        response = table.scan()
        
        for item in response['Items']:
            if item['count'] >= 10:
                filename = item['filename']
                
                # S3에서 파일 이동
                copy_source = {
                    'Bucket': os.environ['DUMMY_BUCKET'],
                    'Key': filename
                }
                s3.copy(copy_source, os.environ['LEARNING_BUCKET'], filename)
                s3.delete_object(Bucket=os.environ['DUMMY_BUCKET'], Key=filename)
                
                # DynamoDB에서 항목 삭제
                table.delete_item(
                    Key={
                        'filename': filename,
                        'label': item['label']
                    }
                )
        
        return {
            'statusCode': 200,
            'body': 'Processing complete'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }