import json
import boto3
import random

s3 = boto3.client('s3')

def handler(event, context):
    try:
        # API Gateway에서 전달된 body 파싱
        body = json.loads(event['body'])
        user_input = body.get('emotion')
        
        # S3에서 랜덤 파일 선택 (실제로는 더 복잡한 로직이 필요할 수 있음)
        bucket_name = "audio-play-chyuni"
        files = s3.list_objects_v2(Bucket=bucket_name)['Contents']
        random_file = random.choice(files)['Key']
        
        # 여기서 실제로는 파일의 정확한 감정을 확인하는 로직이 필요합니다
        correct_emotion = "happy"  # 예시로 "happy"라고 가정
        
        if user_input == correct_emotion:
            return {
                'statusCode': 200,
                'body': json.dumps({'success': True, 'message': 'Captcha verified'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'success': False, 'message': 'Incorrect captcha'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': str(e)})
        }